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
2. For specific mission queries, MATCH the Mission node using case-insensitive `toLower(m.name) CONTAINS toLower(...)`.
3. ALWAYS use `OPTIONAL MATCH (m)-[r]-(n)` to catch ALL connected relationships (organizers, dates, people, locations).
4. Do NOT use aggregated queries like `WITH collect(o)` unless `o` was defined in a MATCH clause.
5. Simple, robust return pattern: `MATCH (m:Mission) WHERE toLower(m.name) CONTAINS toLower("...") OPTIONAL MATCH (m)-[r]-(n) RETURN m, r, n LIMIT 50`

Examples:

Question: "Tell me about Chandrayaan-3 mission, its launch date, and who operated it."
Cypher:
MATCH (m:Mission)
WHERE toLower(m.name) CONTAINS toLower("Chandrayaan-3") or toLower(m.name) CONTAINS toLower("Chandrayaan")
OPTIONAL MATCH (m)-[r]-(n)
RETURN m, r, n
LIMIT 50

Question: "Who is APJ Abdul Kalam?"
Cypher:
MATCH (p:Person)
WHERE toLower(p.name) CONTAINS toLower("Kalam")
OPTIONAL MATCH (p)-[r]-(n)
RETURN p, r, n
LIMIT 50

Return ONLY the raw executable Cypher query. No explanations, no markdown formatting.
"""

LIST_MISSIONS = "MATCH (m:Mission) OPTIONAL MATCH (m)-[r]-(n) RETURN m, r, n LIMIT 30"
LIST_ORGS = "MATCH (o:Organization) OPTIONAL MATCH (o)-[r]-(n) RETURN o, r, n LIMIT 30"
LIST_PEOPLE = "MATCH (p:Person) OPTIONAL MATCH (p)-[r]-(n) RETURN p, r, n LIMIT 30"


def clean_cypher_output(text: str) -> str:
    # Strip markdown blocks
    text = re.sub(r'```(?:cypher)?', '', text).strip()
    
    # Filter out commentary lines
    lines = []
    for line in text.splitlines():
        line_str = line.strip()
        if line_str.lower().startswith(("note:", "explanation:", "//")):
            continue
        lines.append(line_str)
        
    return "\n".join(lines).strip()


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
    cypher_clean = clean_cypher_output(cypher_raw)
    
    return cypher_clean