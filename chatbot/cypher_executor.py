import json
import re
from pathlib import Path
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError, Neo4jError
from chatbot.config import NEO4J_URI, USERNAME, PASSWORD

# Driver instance
try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(USERNAME, PASSWORD)
    )
except Exception:
    driver = None

# Cache for local JSON knowledge base
KB_FILE = Path(__file__).resolve().parent.parent / "data" / "merged" / "final_knowledge_base.json"
_LOCAL_KB_CACHE = None


def load_local_kb():
    global _LOCAL_KB_CACHE
    if _LOCAL_KB_CACHE is not None:
        return _LOCAL_KB_CACHE

    if KB_FILE.exists():
        try:
            with open(KB_FILE, "r", encoding="utf-8") as f:
                _LOCAL_KB_CACHE = json.load(f)
                return _LOCAL_KB_CACHE
        except Exception:
            pass
    _LOCAL_KB_CACHE = []
    return _LOCAL_KB_CACHE


def normalize_label(raw_label: str) -> str:
    if not raw_label:
        return "Entity"
    lbl = str(raw_label).strip().upper()
    mapping = {
        "PERSON": "Scientist",
        "SCIENTIST": "Scientist",
        "ORGANIZATION": "Organization",
        "CENTRE": "Centre",
        "LAUNCH_VEHICLE": "LaunchVehicle",
        "SPACEPORT": "Spaceport",
        "SPACECRAFT": "Spacecraft",
        "PAYLOAD": "Payload",
        "CELESTIAL_BODY": "CelestialBody",
        "MISSION": "Mission"
    }
    return mapping.get(lbl, raw_label.replace("_", " ").title().replace(" ", ""))


def infer_source_type(title: str, rel_source_label: str = None) -> str:
    if rel_source_label:
        norm = normalize_label(rel_source_label)
        if norm in ("Scientist", "Organization", "Centre", "LaunchVehicle", "Mission"):
            return norm

    t_lower = title.lower()
    scientist_keywords = ["kalam", "sarabhai", "dhawan", "somanath", "sivan", "radhakrishnan", "scientist", "pioneer"]
    if any(sk in t_lower for sk in scientist_keywords):
        return "Scientist"
    
    org_keywords = ["isro", "drdo", "department of space", "nasa", "jaxa", "esa"]
    if any(ok == t_lower for ok in org_keywords):
        return "Organization"
        
    centre_keywords = ["space centre", "vssc", "ursc", "sac", "lpsc", "iprc", "istrac", "nrsc"]
    if any(ck in t_lower for ck in centre_keywords):
        return "Centre"

    return "Mission"


def execute_in_memory_search(query: str):
    kb = load_local_kb()
    if not kb:
        return []

    graph_data = []
    q_lower = query.lower()

    # Extract search terms inside quotes or lower match
    matches = re.findall(r'contains\s+tolower\(["\']([^"\']+)["\']\)', q_lower)
    search_term = matches[0].strip() if matches else ""

    if not search_term:
        # Broad ISRO domain keywords list (longer/specific terms first to prevent partial matches)
        domain_keywords = [
            "chandrayaan-3", "chandrayaan 3", "chandrayaan-2", "chandrayaan-1", "chandrayaan-4", "chandrayaan",
            "aditya-l1", "aditya l1", "aditya", "gaganyaan", "spadex", "nisar",
            "mangalyaan", "cartosat", "oceansat", "resourcesat", "risat", "astrosat", "xposat",
            "abdul kalam", "kalam", "sarabhai", "dhawan", "somanath", "sivan", "radhakrishnan",
            "pslv", "gslv", "lvm3", "sslv", "slv-3", "aslv", "aryabhata", "bhaskara", "apple",
            "vssc", "ursc", "shar", "sriharikota", "isro"
        ]
        for kw in domain_keywords:
            if kw in q_lower:
                search_term = kw
                break

    target_missions = []
    
    # 1. Exact Title Match (Highest Precision)
    if search_term:
        term_clean = search_term.replace(" ", "-")
        target_missions = [
            m for m in kb
            if search_term in m.get("title", "").lower()
            or term_clean in m.get("title", "").lower()
            or search_term in m.get("mission_key", "").lower()
        ]
    
    # 2. Content / Entity Fallback Match
    if not target_missions and search_term:
        target_missions = [
            m for m in kb
            if search_term in str(m.get("content", "")).lower()
            or search_term in str(m.get("entities", [])).lower()
        ]

    # Universal Fallback: If no specific search term or query match, return core ISRO graph cluster
    if not target_missions:
        priority_keys = ["chandrayaan-3", "aditya-l1", "gaganyaan", "a.p.j. abdul kalam", "vikram sarabhai"]
        target_missions = [
            m for m in kb if any(pk in m.get("title", "").lower() for pk in priority_keys)
        ]
        if not target_missions:
            target_missions = kb[:5]

    # Limit targets to 2 if specific query to prevent mixing unrelated missions (e.g. Chandrayaan-4 with Chandrayaan-3)
    max_targets = 2 if search_term and search_term != "isro" else 5
    selected_targets = target_missions[:max_targets]

    for mission in selected_targets:
        m_title = mission.get("title", "ISRO Node")
        relationships = mission.get("relationships", [])

        if relationships:
            for rel in relationships[:12]:
                m_type = infer_source_type(m_title, rel.get("source_label") or rel.get("source_type"))
                target_type = normalize_label(rel.get("target_label") or rel.get("target_type"))
                target_name = rel.get("target", "Entity")

                graph_data.append({
                    "m": {
                        "type": m_type,
                        "properties": {"name": m_title}
                    },
                    "r": {
                        "relationship": rel.get("relationship", "RELATED_TO")
                    },
                    "n": {
                        "type": target_type,
                        "properties": {"name": target_name}
                    }
                })
        else:
            m_type = infer_source_type(m_title)
            for ent in mission.get("entities", [])[:8]:
                target_type = normalize_label(ent.get("type", "Entity"))
                target_name = ent.get("name", "Entity")

                graph_data.append({
                    "m": {
                        "type": m_type,
                        "properties": {"name": m_title}
                    },
                    "r": {
                        "relationship": "INVOLVES"
                    },
                    "n": {
                        "type": target_type,
                        "properties": {"name": target_name}
                    }
                })

    return graph_data


def execute_cypher(query: str):
    if not query or not query.strip():
        return execute_in_memory_search("isro")

    graph_data = []

    if driver:
        try:
            with driver.session() as session:
                result = session.run(query)
                records = [dict(record) for record in result]
                if records:
                    return records
        except (CypherSyntaxError, Neo4jError, Exception) as e:
            print(f"[Neo4j Cypher Execution Note]: {e}")

    # Fallback to Universal In-Memory Knowledge Graph Engine
    graph_data = execute_in_memory_search(query)
    if not graph_data:
        graph_data = execute_in_memory_search("isro")

    return graph_data