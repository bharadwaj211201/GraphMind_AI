from chatbot.llm_interface import ask_llm


def generate_cypher(question):

    prompt = f"""
You are an expert Neo4j Cypher developer.

You MUST generate Cypher ONLY.

=========================
DATABASE SCHEMA
=========================

Nodes

Mission
Organization
Person
Location
Date

Properties

Mission.name
Organization.name
Person.name
Location.name
Date.name

Relationships

(Mission)-[:HAS_ORGANIZATION]->(Organization)

(Mission)-[:HAS_PERSON]->(Person)

(Mission)-[:HAS_LOCATION]->(Location)

(Mission)-[:HAS_DATE]->(Date)

=========================
RULES
=========================

1. Never invent node labels.

2. Never invent relationships.

3. Never invent properties.

4. NEVER use
(Organization)-[:HAS_LOCATION]->(Location)

5. ALWAYS search mission using

WHERE toLower(m.name) CONTAINS toLower("<mission>")

6. Always use OPTIONAL MATCH.

7. Return ONLY Cypher.

8. No explanation.

9. No markdown.

10. End query with RETURN.

=========================
Example
=========================

Question

Tell me about Chandrayaan-3

Cypher

MATCH (m:Mission)
WHERE toLower(m.name) CONTAINS toLower("Chandrayaan-3")

OPTIONAL MATCH (m)-[:HAS_ORGANIZATION]->(o:Organization)
OPTIONAL MATCH (m)-[:HAS_PERSON]->(p:Person)
OPTIONAL MATCH (m)-[:HAS_LOCATION]->(l:Location)
OPTIONAL MATCH (m)-[:HAS_DATE]->(d:Date)

RETURN
m.name AS Mission,
collect(DISTINCT o.name) AS Organizations,
collect(DISTINCT p.name) AS People,
collect(DISTINCT l.name) AS Locations,
collect(DISTINCT d.name) AS Dates

=========================

Question

{question}
"""

    cypher = ask_llm(prompt)

    cypher = cypher.replace("```cypher", "")
    cypher = cypher.replace("```", "")

    return cypher.strip()