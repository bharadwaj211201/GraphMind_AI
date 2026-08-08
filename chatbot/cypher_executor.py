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
        # Broad ISRO domain keywords list
        domain_keywords = [
            "kalam", "abdul kalam", "sarabhai", "dhawan", "somanath", "sivan", "radhakrishnan",
            "chandrayaan-3", "chandrayaan", "aditya-l1", "aditya", "gaganyaan", "spadex", "nisar",
            "mangalyaan", "cartosat", "oceansat", "resourcesat", "risat", "astrosat", "xposat",
            "isro", "pslv", "gslv", "lvm3", "sslv", "slv-3", "aslv", "aryabhata", "bhaskara", "apple",
            "vssc", "ursc", "shar", "sriharikota", "payload", "rocket", "satellite", "orbit", "moon", "mars", "sun"
        ]
        for kw in domain_keywords:
            if kw in q_lower:
                search_term = kw
                break

    target_missions = []
    if search_term:
        target_missions = [
            m for m in kb
            if search_term in m.get("title", "").lower()
            or search_term in m.get("mission_key", "").lower()
            or search_term in str(m.get("content", "")).lower()
            or search_term in str(m.get("entities", [])).lower()
            or search_term in str(m.get("relationships", [])).lower()
        ]

    # Universal Fallback: If no specific search term or query match, return core ISRO graph cluster
    if not target_missions:
        priority_keys = ["chandrayaan-3", "aditya-l1", "gaganyaan", "a.p.j. abdul kalam", "vikram sarabhai", "isro"]
        target_missions = [
            m for m in kb if any(pk in m.get("title", "").lower() for pk in priority_keys)
        ]
        if not target_missions:
            target_missions = kb[:8]

    for mission in target_missions[:8]:
        m_title = mission.get("title", "ISRO Mission")
        relationships = mission.get("relationships", [])

        if relationships:
            for rel in relationships[:10]:
                graph_data.append({
                    "m": {
                        "type": "Mission",
                        "properties": {"name": m_title}
                    },
                    "r": {
                        "relationship": rel.get("relationship", "RELATED_TO")
                    },
                    "n": {
                        "type": rel.get("target_label", "Entity"),
                        "properties": {"name": rel.get("target", "Entity")}
                    }
                })
        else:
            for ent in mission.get("entities", [])[:8]:
                graph_data.append({
                    "m": {
                        "type": "Mission",
                        "properties": {"name": m_title}
                    },
                    "r": {
                        "relationship": "INVOLVES"
                    },
                    "n": {
                        "type": ent.get("type", "Entity").title(),
                        "properties": {"name": ent.get("name", "Entity")}
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