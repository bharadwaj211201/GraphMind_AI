import ollama

SCHEMA = """
You are an expert Neo4j Cypher Generator.

Database Schema

Nodes:
- Mission
- Organization
- Person
- Location
- Date

Relationships:
- (Mission)-[:HAS_ORGANIZATION]->(Organization)
- (Mission)-[:HAS_PERSON]->(Person)
- (Mission)-[:HAS_LOCATION]->(Location)
- (Mission)-[:HAS_DATE]->(Date)

Rules:

1. Output ONLY Cypher.
2. No explanations.
3. No markdown.
4. Never use CREATE.
5. Never use DELETE.
6. Never use MERGE.
7. Never use DROP.
8. Never use exact node matching like:
   MATCH (m:Mission {name:"..."})

9. Always search using:

   WHERE toLower(m.name) CONTAINS toLower("keyword")

10. Always retrieve every available relation.

Example:

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
LIMIT 5
"""


def generate_cypher(question):

    prompt = f"""
{SCHEMA}

User Question:
{question}

Generate ONLY the Cypher query.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    cypher = response["message"]["content"]

    cypher = cypher.replace("```cypher", "")
    cypher = cypher.replace("```", "")
    cypher = cypher.strip()

    return cypher