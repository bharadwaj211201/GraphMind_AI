import re
from chatbot.llm_interface import ask_llm
from chatbot.intent_classifier import get_intent

MISSION_PROMPT = """
You are a Cypher query generator for a Neo4j ISRO Knowledge Graph.

Database Node Labels and Properties:
- Node (:Mission) has property 'name'
- Node (:Organization) has property 'name'
- Node (:Person) has property 'name'
- Node (:Date) has property 'name' or 'value'
- Node (:Location) has property 'name'

CRITICAL RULES FOR GENERATING CYPHER:
1. Every variable used in RETURN or WITH clauses MUST be defined in a prior MATCH clause.
2. For specific mission, person, or organization queries, MATCH the target node using case-insensitive `toLower(m.name) CONTAINS toLower(...)`.
3. ALWAYS use `OPTIONAL MATCH (m)-[r]-(n)` to catch ALL connected relationships (organizations, dates, people, locations).
4. Do NOT restrict queries to `:Mission` if the user is asking about a Person (e.g. Vikram Sarabhai, Kalam) or Organization (e.g. ISRO). Match any node label `(m)`: `MATCH (m) WHERE toLower(m.name) CONTAINS toLower("...") OPTIONAL MATCH (m)-[r]-(n) RETURN m, r, n LIMIT 50`
5. Simple, robust return pattern: `MATCH (m) WHERE toLower(m.name) CONTAINS toLower("...") OPTIONAL MATCH (m)-[r]-(n) RETURN m, r, n LIMIT 50`

Return ONLY the raw executable Cypher query. No explanations, no markdown formatting.
"""

LIST_MISSIONS = "MATCH (m:Mission) OPTIONAL MATCH (m)-[r]-(n) RETURN m, r, n LIMIT 30"
LIST_ORGS = "MATCH (o:Organization) OPTIONAL MATCH (o)-[r]-(n) RETURN o, r, n LIMIT 30"
LIST_PEOPLE = "MATCH (p:Person) OPTIONAL MATCH (p)-[r]-(n) RETURN p, r, n LIMIT 30"


def clean_cypher_output(text: str) -> str:
    text = re.sub(r'```(?:cypher)?', '', text).strip()
    lines = []
    for line in text.splitlines():
        line_str = line.strip()
        if line_str.lower().startswith(("note:", "explanation:", "//")):
            continue
        lines.append(line_str)
    return "\n".join(lines).strip()


def extract_fallback_keyword(question: str) -> str:
    q_low = question.lower()

    # 1. Pioneer & Scientist Entities
    pioneer_map = {
        "sarabhai": "sarabhai", "vikram": "sarabhai",
        "kalam": "kalam", "abdul kalam": "kalam",
        "dhawan": "dhawan", "satish dhawan": "dhawan",
        "somanath": "somanath", "sivan": "sivan",
        "radhakrishnan": "radhakrishnan", "u.r. rao": "ur rao", "ur rao": "ur rao",
        "kasturirangan": "kasturirangan", "annadurai": "annadurai", "bhabha": "bhabha"
    }
    for key, kw_target in pioneer_map.items():
        if key in q_low:
            return kw_target

    # 2. Historic Milestones & Latest Mission Keywords
    if any(w in q_low for w in ["last rocket", "last launch", "latest rocket", "latest launch", "recent rocket", "recent launch", "most recent rocket", "last rocket launched"]):
        return "spadex"
    if any(w in q_low for w in ["latest", "recent", "upcoming", "newest", "current project", "current mission"]):
        return "chandrayaan-3"
    if any(w in q_low for w in ["first successful mission", "first successful satellite", "first successful launch"]):
        return "rohini"
    if any(w in q_low for w in ["first mission", "first satellite", "first space mission", "first spacecraft", "first isro mission", "first isro satellite", "initial mission"]):
        return "aryabhata"
    if any(w in q_low for w in ["first moon", "first lunar"]):
        return "chandrayaan-1"
    if any(w in q_low for w in ["first mars", "first interplanetary"]):
        return "mangalyaan"
    if any(w in q_low for w in ["first solar", "first sun"]):
        return "aditya-l1"
    if any(w in q_low for w in ["first rocket", "first launch vehicle"]):
        return "slv-3"

    # 3. Founder, Chairman & Astronaut Keywords
    if any(w in q_low for w in ["shukla", "shubhanshu", "axiom", "axiom-4", "axiom 4"]):
        return "shubhanshu shukla"
    if any(w in q_low for w in ["current chairman", "who is chairman", "present chairman", "isro chairman", "head of isro", "narayanan", "dr v narayanan", "dr. v. narayanan", "v narayanan", "somanath", "s. somanath", "chairman"]):
        return "narayanan"
    if any(w in q_low for w in ["where is isro", "isro located", "isro headquarters", "headquarters of isro", "isro head office", "isro location", "where is isro headquarter"]):
        return "isro headquarters"
    if any(w in q_low for w in ["founder", "founded", "father of isro", "father of indian space", "who created isro", "who started isro", "who established isro", "establishment of isro"]):
        return "sarabhai"

    # 4. Specific Spacecraft Missions & Satellites
    mission_targets = [
        "chandrayaan-3", "chandrayaan 3", "chandrayaan-2", "chandrayaan-1", "chandrayaan-4", "chandrayaan",
        "aditya-l1", "aditya l1", "aditya", "gaganyaan", "shubhanshu shukla", "axiom-4", "mangalyaan-2", "mangalyaan", "mars orbiter mission", "mom",
        "astrosat", "xposat", "spadex", "lupex", "shukrayaan", "nisar", "trishna", "gsat-n2", "insat-3ds",
        "cartosat-3", "cartosat-2", "cartosat-1", "cartosat", "oceansat-3", "oceansat-2", "oceansat-1", "oceansat",
        "resourcesat", "risat-2b", "risat-2", "risat-1", "risat", "eos-08", "eos-07", "eos-06", "eos-05", "eos-04",
        "eos-03", "eos-02", "eos-01", "eos", "aryabhata", "bhaskara", "apple", "oneweb", "gsat", "insat"
    ]
    for st in mission_targets:
        if st in q_low:
            return st.replace(" ", "-")

    # 4. Specific Launch Vehicles & Rockets
    vehicle_targets = ["pslv-c58", "pslv-c57", "pslv-c37", "pslv-c11", "pslv-c25", "pslv", "lvm3-m4", "lvm3-m1", "lvm3", "gslv-f14", "gslv", "sslv-d3", "sslv-d2", "sslv", "slv-3", "aslv"]
    for vt in vehicle_targets:
        if vt in q_low:
            return vt.replace(" ", "-")

    # 5. Specific Research Centres & Spaceports
    centre_targets = ["sriharikota", "sdsc", "shar", "vssc", "ursc", "sac", "lpsc", "iprc", "nrsc", "istrac", "terls", "space applications centre", "vikram sarabhai space centre", "u r rao satellite centre"]
    for ct in centre_targets:
        if ct in q_low:
            return ct.replace(" ", "-")

    # 6. Specific Payloads
    payload_targets = ["chaste", "ilsa", "papa", "polix", "xspect", "mcc", "m3", "velc", "suit", "solexs", "hel1os"]
    for pt in payload_targets:
        if pt in q_low:
            return pt

    # 7. General ISRO entity check
    if "isro" in q_low:
        if any(w in q_low for w in ["who", "founder", "start", "father", "head", "creator"]):
            return "sarabhai"
        return "isro"

    # 8. Dynamic Stop Words Extraction
    stop_words = {
        "tell", "about", "what", "where", "when", "which", "show", "list", "give", "from",
        "who", "whom", "founded", "founder", "father", "isro", "does", "have", "many",
        "created", "started", "established", "scientific", "payloads", "payload",
        "mission", "satellite", "launch", "space", "vehicle", "rocket"
    }
    words = [w.strip("?,.!\"':;") for w in question.split() if len(w) > 3 and w.lower() not in stop_words]
    if words:
        return words[0]

    return "list_missions"


def generate_cypher(question: str) -> str:
    intent = get_intent(question)

    if intent == "list_missions":
        return LIST_MISSIONS
    elif intent == "list_people":
        return LIST_PEOPLE
    elif intent == "list_organizations":
        return LIST_ORGS

    prompt = f"{MISSION_PROMPT}\n\nUser Question: \"{question}\"\n\nCypher Query:"
    cypher_raw = ask_llm(prompt)

    if "[OLLAMA_ERROR]" in cypher_raw:
        kw = extract_fallback_keyword(question)
        if kw == "list_missions":
            return LIST_MISSIONS
        return f'MATCH (m) WHERE toLower(m.name) CONTAINS toLower("{kw}") OPTIONAL MATCH (m)-[r]-(n) RETURN m, r, n LIMIT 50'

    cypher_clean = clean_cypher_output(cypher_raw)
    return cypher_clean