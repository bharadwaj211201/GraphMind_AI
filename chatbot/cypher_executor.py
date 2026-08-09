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


def get_all_kb_missions() -> list:
    kb = load_local_kb()
    missions = []
    seen = set()
    for item in kb:
        title = item.get("title", "").strip()
        if is_actual_mission(title) and title.lower() not in seen:
            seen.add(title.lower())
            missions.append(title)
    return missions


def execute_in_memory_search(query: str):
    kb = load_local_kb()
    if not kb:
        return []

    graph_data = []
    q_lower = query.lower().strip()

    # Detect list_missions intent or broad mission query
    is_list_missions = any(phrase in q_lower for phrase in ["list all", "list mission", "all mission", "show mission", "list_missions", "match (m:mission)", "match (m:spacecraft)", "directory"])
    if is_list_missions:
        return [
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "LUNAR_PROGRAM"}, "n": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "SOLAR_PROGRAM"}, "n": {"type": "Mission", "properties": {"name": "Aditya-L1"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "PLANETARY_PROGRAM"}, "n": {"type": "Mission", "properties": {"name": "Mars Orbiter Mission (Mangalyaan)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "HUMAN_SPACEFLIGHT"}, "n": {"type": "Mission", "properties": {"name": "Gaganyaan Program"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "ASTRONOMY_OBSERVATORY"}, "n": {"type": "Mission", "properties": {"name": "XPoSat & AstroSat"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "EARTH_OBSERVATION"}, "n": {"type": "Mission", "properties": {"name": "EOS-08 & Cartosat-3"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "COMMUNICATION_SATELLITE"}, "n": {"type": "Mission", "properties": {"name": "GSAT-N2 & INSAT-3DS"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "NAVIGATION_SYSTEM"}, "n": {"type": "Mission", "properties": {"name": "NavIC (IRNSS) & NVS-01"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "TECH_DEMONSTRATOR"}, "n": {"type": "Mission", "properties": {"name": "SpaDeX & RLV-TD"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "HISTORIC_FIRST"}, "n": {"type": "Mission", "properties": {"name": "Aryabhata (1975)"}}}
        ]

    # Special Location Graph Handler (renders ISRO HQ & Location nodes on interactive graph canvas)
    if any(w in q_lower for w in ["where is isro", "isro located", "isro headquarters", "headquarters of isro", "isro head office", "isro location", "headquarter"]):
        return [
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "LOCATED_AT"}, "n": {"type": "Location", "properties": {"name": "Antariksh Bhavan, Bengaluru"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "GOVERNED_BY"}, "n": {"type": "Organization", "properties": {"name": "Department of Space (DOS)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Spaceport", "properties": {"name": "Satish Dhawan Space Centre (Sriharikota, AP)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Centre", "properties": {"name": "U R Rao Satellite Centre (URSC, Bengaluru)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Centre", "properties": {"name": "Vikram Sarabhai Space Centre (VSSC, Thiruvananthapuram)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Centre", "properties": {"name": "Space Applications Centre (SAC, Ahmedabad)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Centre", "properties": {"name": "Liquid Propulsion Systems Centre (LPSC, Valiamala)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Centre", "properties": {"name": "ISTRAC (Bengaluru)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO Headquarters"}}, "r": {"relationship": "OPERATES_CENTRE"}, "n": {"type": "Centre", "properties": {"name": "National Remote Sensing Centre (NRSC, Hyderabad)"}}}
        ]

    # Special Chairman & Leadership Graph Handler
    if any(w in q_lower for w in ["chairman", "present chairman", "current chairman", "head of isro", "narayanan", "v narayanan", "dr v narayanan", "somanath", "s. somanath"]):
        return [
            {"m": {"type": "Scientist", "properties": {"name": "Dr. V. Narayanan"}}, "r": {"relationship": "CURRENT_CHAIRMAN_OF"}, "n": {"type": "Organization", "properties": {"name": "ISRO"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Dr. V. Narayanan"}}, "r": {"relationship": "SECRETARY_OF"}, "n": {"type": "Organization", "properties": {"name": "Department of Space (DOS)"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Dr. V. Narayanan"}}, "r": {"relationship": "FORMER_DIRECTOR_OF"}, "n": {"type": "Centre", "properties": {"name": "Liquid Propulsion Systems Centre (LPSC)"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Shri S. Somanath"}}, "r": {"relationship": "FORMER_CHAIRMAN_OF"}, "n": {"type": "Organization", "properties": {"name": "ISRO"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Dr. K. Sivan"}}, "r": {"relationship": "FORMER_CHAIRMAN_OF"}, "n": {"type": "Organization", "properties": {"name": "ISRO"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Dr. Vikram Sarabhai"}}, "r": {"relationship": "FOUNDER_AND_FIRST_CHAIRMAN"}, "n": {"type": "Organization", "properties": {"name": "ISRO"}}}
        ]

    # Special Chandrayaan-3 Graph Handler (renders comprehensive Chandrayaan-3 graph)
    if any(w in q_lower for w in ["chandrayaan-3", "chandrayaan 3", "chandrayaan3"]):
        return [
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "LAUNCHED_BY"}, "n": {"type": "LaunchVehicle", "properties": {"name": "LVM3-M4 Heavy Rocket"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "LAUNCHED_ON"}, "n": {"type": "Date", "properties": {"name": "14 July 2023"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "LANDED_AT"}, "n": {"type": "CelestialBody", "properties": {"name": "Shiv Shakti Point (Lunar South Pole)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "CARRIES_LANDER"}, "n": {"type": "Spacecraft", "properties": {"name": "Vikram Lander"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "CARRIES_ROVER"}, "n": {"type": "Spacecraft", "properties": {"name": "Pragyan Rover"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "CARRIES_PAYLOAD"}, "n": {"type": "Payload", "properties": {"name": "ChaSTE (Surface Thermophysics)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "CARRIES_PAYLOAD"}, "n": {"type": "Payload", "properties": {"name": "RAMBHA-LP (Plasma Density)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "CARRIES_PAYLOAD"}, "n": {"type": "Payload", "properties": {"name": "ILSA (Lunar Seismic Activity)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "CARRIES_PAYLOAD"}, "n": {"type": "Payload", "properties": {"name": "APXS & LIBS (Elemental Analysis)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "DEVELOPED_AT"}, "n": {"type": "Centre", "properties": {"name": "U R Rao Satellite Centre (URSC)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "LAUNCHED_FROM"}, "n": {"type": "Spaceport", "properties": {"name": "Satish Dhawan Space Centre (SDSC SHAR)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "MANAGED_BY"}, "n": {"type": "Scientist", "properties": {"name": "P. Veeramuthuvel (Project Director)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}, "r": {"relationship": "SPEARHEADED_BY"}, "n": {"type": "Scientist", "properties": {"name": "Shri S. Somanath (ISRO Chairman)"}}}
        ]

    # Special Shubhanshu Shukla & Gaganyaan Astronaut Graph Handler
    if any(w in q_lower for w in ["shukla", "shubhanshu", "axiom", "axiom-4", "axiom 4"]):
        return [
            {"m": {"type": "Scientist", "properties": {"name": "Group Captain Shubhanshu Shukla"}}, "r": {"relationship": "PRIME_ASTRONAUT_FOR"}, "n": {"type": "Mission", "properties": {"name": "Axiom-4 (Ax-4) ISS Mission"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Group Captain Shubhanshu Shukla"}}, "r": {"relationship": "DESIGNATED_ASTRONAUT_OF"}, "n": {"type": "Mission", "properties": {"name": "Gaganyaan Human Spaceflight Program"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Group Captain Shubhanshu Shukla"}}, "r": {"relationship": "TRAINED_AT"}, "n": {"type": "Organization", "properties": {"name": "NASA Johnson Space Center"}}},
            {"m": {"type": "Scientist", "properties": {"name": "Group Captain Shubhanshu Shukla"}}, "r": {"relationship": "TRAINED_AT"}, "n": {"type": "Organization", "properties": {"name": "Yuri Gagarin Cosmonaut Training Center"}}},
            {"m": {"type": "Mission", "properties": {"name": "Gaganyaan"}}, "r": {"relationship": "EXECUTED_BY"}, "n": {"type": "Organization", "properties": {"name": "ISRO"}}},
            {"m": {"type": "Mission", "properties": {"name": "Gaganyaan"}}, "r": {"relationship": "DEVELOPED_AT"}, "n": {"type": "Centre", "properties": {"name": "Human Space Flight Centre (HSFC)"}}},
            {"m": {"type": "Mission", "properties": {"name": "Gaganyaan"}}, "r": {"relationship": "LAUNCHED_BY"}, "n": {"type": "LaunchVehicle", "properties": {"name": "LVM3 (Human Rated)"}}}
        ]

    # Special List All Missions / Directory Graph Handler
    if any(w in q_lower for w in ["list all missions", "all space missions", "directory of missions", "list all space missions", "show all missions", "complete directory"]):
        return [
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "LUNAR_PROGRAM"}, "n": {"type": "Mission", "properties": {"name": "Chandrayaan-3"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "SOLAR_PROGRAM"}, "n": {"type": "Mission", "properties": {"name": "Aditya-L1"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "PLANETARY_PROGRAM"}, "n": {"type": "Mission", "properties": {"name": "Mars Orbiter Mission (Mangalyaan)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "HUMAN_SPACEFLIGHT"}, "n": {"type": "Mission", "properties": {"name": "Gaganyaan Program"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "ASTRONOMY_OBSERVATORY"}, "n": {"type": "Mission", "properties": {"name": "XPoSat & AstroSat"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "EARTH_OBSERVATION"}, "n": {"type": "Mission", "properties": {"name": "EOS-08 & Cartosat-3"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "COMMUNICATION_SATELLITE"}, "n": {"type": "Mission", "properties": {"name": "GSAT-N2 & INSAT-3DS"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "NAVIGATION_SYSTEM"}, "n": {"type": "Mission", "properties": {"name": "NavIC (IRNSS) & NVS-01"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "TECH_DEMONSTRATOR"}, "n": {"type": "Mission", "properties": {"name": "SpaDeX & RLV-TD"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "HISTORIC_FIRST"}, "n": {"type": "Mission", "properties": {"name": "Aryabhata (1975)"}}}
        ]

    # Special Last Rocket / Recent Launch Graph Handler
    if any(w in q_lower for w in ["last rocket", "last launch", "latest rocket", "latest launch", "recent rocket", "recent launch", "most recent rocket", "last rocket launched"]):
        return [
            {"m": {"type": "LaunchVehicle", "properties": {"name": "PSLV-C60"}}, "r": {"relationship": "LAUNCHED_SPACECRAFT"}, "n": {"type": "Mission", "properties": {"name": "SpaDeX (30 Dec 2024)"}}},
            {"m": {"type": "LaunchVehicle", "properties": {"name": "Falcon 9 (SpaceX)"}}, "r": {"relationship": "LAUNCHED_SPACECRAFT"}, "n": {"type": "Mission", "properties": {"name": "GSAT-N2 (19 Nov 2024)"}}},
            {"m": {"type": "LaunchVehicle", "properties": {"name": "SSLV-D3"}}, "r": {"relationship": "LAUNCHED_SPACECRAFT"}, "n": {"type": "Mission", "properties": {"name": "EOS-08 (16 Aug 2024)"}}},
            {"m": {"type": "LaunchVehicle", "properties": {"name": "GSLV-F14"}}, "r": {"relationship": "LAUNCHED_SPACECRAFT"}, "n": {"type": "Mission", "properties": {"name": "INSAT-3DS (17 Feb 2024)"}}},
            {"m": {"type": "LaunchVehicle", "properties": {"name": "PSLV-C58"}}, "r": {"relationship": "LAUNCHED_SPACECRAFT"}, "n": {"type": "Mission", "properties": {"name": "XPoSat (01 Jan 2024)"}}},
            {"m": {"type": "Organization", "properties": {"name": "ISRO"}}, "r": {"relationship": "OPERATES_SPACEPORT"}, "n": {"type": "Spaceport", "properties": {"name": "Satish Dhawan Space Centre (Sriharikota)"}}}
        ]

    # Extract search terms inside quotes or lower match
    matches = re.findall(r'contains\s+tolower\(["\']([^"\']+)["\']\)', q_lower)
    cypher_term = matches[0].strip() if matches else ""

    # Stop words list for token extraction (including Cypher syntax keywords)
    stop_words = {
        "tell", "about", "what", "where", "when", "which", "show", "list", "give", "from",
        "who", "whom", "does", "have", "many", "created", "started", "established", "the",
        "is", "are", "was", "were", "an", "a", "and", "or", "in", "on", "at", "to", "for",
        "of", "with", "by", "how", "can", "you", "me", "please", "detail", "details",
        "match", "where", "tolower", "contains", "optional", "return", "limit", "name"
    }

    # Extract query tokens
    query_tokens = [w.strip("?,.!\"':;()") for w in q_lower.split() if len(w) > 2 and w.lower() not in stop_words]
    if cypher_term and cypher_term not in stop_words:
        query_tokens.append(cypher_term)

    # Special Keyword Mapping for Founder/Pioneers/Rockets/Sites
    if cypher_term in {"founded", "founder", "father", "creator", "started", "established"} or any(w in q_lower for w in ["founder", "founded", "father of isro", "father of indian space", "who created isro", "who started isro", "who established isro"]):
        query_tokens.append("sarabhai")
    elif any(w in q_lower for w in ["kalam", "abdul kalam"]):
        query_tokens.append("kalam")
    elif any(w in q_lower for w in ["sarabhai", "vikram"]):
        query_tokens.append("sarabhai")
    elif any(w in q_lower for w in ["dhawan"]):
        query_tokens.append("dhawan")

    # Score each document in KB
    scored_items = []
    for item in kb:
        title = item.get("title", "").lower()
        m_key = item.get("mission_key", "").lower()
        cat = item.get("category", "").lower()
        content = str(item.get("documents", [])).lower() + " " + str(item.get("entities", [])).lower()
        rel_str = str(item.get("relationships", [])).lower()

        norm_cypher = cypher_term.replace("-", "").replace(" ", "").lower() if cypher_term else ""
        norm_title = title.replace("-", "").replace(" ", "").lower()
        norm_mkey = m_key.replace("-", "").replace(" ", "").lower()

        score = 0
        
        # Cypher term exact / normalized match boost
        if norm_cypher and (norm_cypher in norm_title or norm_cypher in norm_mkey or norm_title in norm_cypher):
            score += 100

        for token in query_tokens:
            token_norm = token.replace("-", "").replace(" ", "").lower()
            if token_norm and (token_norm in norm_title or token_norm in norm_mkey):
                score += 80
            elif token in title or token in m_key:
                score += 40
            elif token in cat:
                score += 20
            elif token in rel_str:
                score += 15
            elif token in content:
                score += 10

        if score > 0:
            scored_items.append((score, item))

    # Sort by score descending
    scored_items.sort(key=lambda x: x[0], reverse=True)
    target_missions = [item for _, item in scored_items]

    # Universal Fallback: If no specific search term or query match, return relevant ISRO graph cluster
    if not target_missions:
        if any(w in q_lower for w in ["who", "person", "scientist", "founder", "father", "established", "created"]):
            priority_keys = ["vikram sarabhai", "a.p.j. abdul kalam", "satish dhawan"]
        else:
            priority_keys = ["chandrayaan-3", "aditya-l1", "gaganyaan", "a.p.j. abdul kalam", "vikram sarabhai"]
        target_missions = [
            m for m in kb if any(pk in m.get("title", "").lower() for pk in priority_keys)
        ]
        if not target_missions:
            target_missions = kb[:3]

    # Focus strictly on the single highest-scoring main target entity for specific queries
    # This prevents unrelated mission nodes from polluting the graph canvas with noise.
    if cypher_term or query_tokens:
        max_targets = 1
    else:
        max_targets = 5
    selected_targets = target_missions[:max_targets]

    for mission in selected_targets:
        m_title = mission.get("title", "ISRO Node")
        relationships = mission.get("relationships", [])

        if relationships:
            # Return up to 15 relationships per node for rich visual network
            for rel in relationships[:15]:
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
            for ent in mission.get("entities", [])[:10]:
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
    is_list_missions = any(phrase in q_low for phrase in ["list all", "list mission", "all mission", "show mission", "list_missions", "match (m:mission)", "directory"])
    if is_list_missions:
        return records

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

        # If user asked to list missions, keep ISRO hub node or actual space missions!
        if is_list_missions:
            if m_name.upper() != "ISRO" and not is_actual_mission(m_name):
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