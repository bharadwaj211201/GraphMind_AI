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


KNOWN_SCIENTISTS = [
    "kalam", "abdul kalam", "sarabhai", "dhawan", "somanath", "sivan", "radhakrishnan",
    "u.r. rao", "ur rao", "u r rao", "kasturirangan", "annadurai", "bhabha", "homi"
]

KNOWN_ORGS = [
    "isro", "drdo", "department of space", "nasa", "jaxa", "esa", "prl",
    "physical research laboratory", "indian institute of science", "iisc"
]

KNOWN_CENTRES = [
    "space centre", "vssc", "ursc", "sac", "lpsc", "iprc", "istrac", "nrsc", "shar"
]

KNOWN_MISSIONS = [
    "chandrayaan", "aditya", "gaganyaan", "mangalyaan", "astrosat", "xposat",
    "spadex", "lupex", "cartosat", "oceansat", "resourcesat", "risat", "eos",
    "aryabhata", "bhaskara", "apple", "insat", "gsat", "nisar", "trishna", "shukrayaan"
]


def is_actual_mission(name: str) -> bool:
    if not name:
        return False
    n_low = name.strip().lower()

    # Exclude scientists / people
    if any(s in n_low for s in KNOWN_SCIENTISTS):
        return False

    # Exclude orgs and centres
    if any(o in n_low for o in KNOWN_ORGS + KNOWN_CENTRES):
        return False

    # Positive match for mission patterns
    return any(m in n_low for m in KNOWN_MISSIONS)


def infer_source_type(title: str, rel_source_label: str = None) -> str:
    t_lower = title.strip().lower()

    # 1. Highest Priority: Keyword matching on title
    if any(sk in t_lower for sk in KNOWN_SCIENTISTS):
        return "Scientist"
    if any(ok == t_lower or t_lower.startswith(ok) for ok in KNOWN_ORGS):
        return "Organization"
    if any(ck in t_lower for ck in KNOWN_CENTRES):
        return "Centre"
    if any(mk in t_lower for mk in KNOWN_MISSIONS):
        return "Mission"

    # 2. Second Priority: rel_source_label if provided
    if rel_source_label:
        norm = normalize_label(rel_source_label)
        if norm in ("Scientist", "Organization", "Centre", "LaunchVehicle", "Mission"):
            return norm

    return "Mission"


def execute_in_memory_search(query: str):
    kb = load_local_kb()
    if not kb:
        return []

    graph_data = []
    q_lower = query.lower()

    # Detect list_missions intent or broad mission query
    is_list_missions = any(phrase in q_lower for phrase in ["list all", "list mission", "all mission", "show mission", "list_missions", "match (m:mission)"])

    if is_list_missions:
        mission_records = []
        seen_titles = set()

        for m in kb:
            title = m.get("title", "").strip()
            if is_actual_mission(title) and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                mission_records.append(title)

        selected_titles = mission_records[:8] if mission_records else ["Chandrayaan-3", "Aditya-L1", "Gaganyaan", "Mangalyaan", "AstroSat", "XPoSat", "SpaDeX", "EOS-06"]

        for m_title in selected_titles:
            graph_data.append({
                "m": {
                    "type": "Mission",
                    "properties": {"name": m_title}
                },
                "r": {
                    "relationship": "DEVELOPED_BY"
                },
                "n": {
                    "type": "Organization",
                    "properties": {"name": "ISRO"}
                }
            })
        return graph_data

    # Extract search terms inside quotes or lower match
    matches = re.findall(r'contains\s+tolower\(["\']([^"\']+)["\']\)', q_lower)
    search_term = matches[0].strip() if matches else ""

    if not search_term:
        # Broad ISRO domain keywords list
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
            target_missions = kb[:3]

    # Limit target entity documents to 1 for specific query to keep graph clean and uncrowded
    max_targets = 1 if search_term and search_term != "isro" else 3
    selected_targets = target_missions[:max_targets]

    for mission in selected_targets:
        m_title = mission.get("title", "ISRO Node")
        relationships = mission.get("relationships", [])

        if relationships:
            # Cap relationships to 6 max per node to prevent graph overcrowding
            for rel in relationships[:6]:
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
            for ent in mission.get("entities", [])[:5]:
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



def sanitize_graph_records(records: list, query: str = "") -> list:
    if not records:
        return []

    q_low = query.lower()
    is_list_missions = any(phrase in q_low for phrase in ["list all", "list mission", "all mission", "show mission", "list_missions", "match (m:mission)"])

    sanitized = []
    seen_keys = set()

    for item in records:
        if not isinstance(item, dict):
            continue

        m = item.get("m", {})
        r = item.get("r", {})
        n = item.get("n", {})

        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}

        m_name = str(m_props.get("name", m_props.get("title", ""))).strip()
        n_name = str(n_props.get("name", n_props.get("title", ""))).strip()

        if not m_name:
            continue

        # Correct type inference
        m_type = infer_source_type(m_name, m.get("type") if isinstance(m, dict) else None)
        n_type = normalize_label(n.get("type") if isinstance(n, dict) else "Entity")

        # If user asked to list missions, STRICTLY filter for actual space missions!
        if is_list_missions:
            if not is_actual_mission(m_name):
                continue

        key = (m_name, n_name, r.get("relationship") if isinstance(r, dict) else "")
        if key in seen_keys:
            continue
        seen_keys.add(key)

        sanitized.append({
            "m": {
                "type": m_type,
                "properties": {"name": m_name}
            },
            "r": {
                "relationship": r.get("relationship", "RELATED_TO") if isinstance(r, dict) else "RELATED_TO"
            },
            "n": {
                "type": n_type,
                "properties": {"name": n_name}
            }
        })

    return sanitized


def execute_cypher(query: str):
    if not query or not query.strip():
        return sanitize_graph_records(execute_in_memory_search("isro"), "isro")

    if driver:
        try:
            with driver.session() as session:
                result = session.run(query)
                records = [dict(record) for record in result]
                if records:
                    return sanitize_graph_records(records, query)
        except (CypherSyntaxError, Neo4jError, Exception) as e:
            print(f"[Neo4j Cypher Execution Note]: {e}")

    # Fallback to Universal In-Memory Knowledge Graph Engine
    graph_data = execute_in_memory_search(query)
    if not graph_data:
        graph_data = execute_in_memory_search("isro")

    return sanitize_graph_records(graph_data, query)