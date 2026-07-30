from pymongo import MongoClient
from neo4j import GraphDatabase

# =====================================================
# MongoDB Configuration
# =====================================================

mongo_client = MongoClient("mongodb://localhost:27017/")

mongo_db = mongo_client["graphmind_ai"]

collection = mongo_db["website_entities"]

# =====================================================
# Neo4j Configuration
# =====================================================

URI = "neo4j://127.0.0.1:7687"

USERNAME = "neo4j"

PASSWORD = "graphmind123"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

# =====================================================
# Connect
# =====================================================

print("=" * 60)
print("GRAPHMIND AI - NEO4J LOADER")
print("=" * 60)

with driver.session() as session:
    session.run("RETURN 1")

print("[OK] Connected to Neo4j")

# =====================================================
# Clear Existing Graph
# =====================================================

print("Clearing old graph...")

with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

print("[OK] Graph Cleared")

# =====================================================
# Read MongoDB
# =====================================================

documents = list(collection.find())

print(f"[OK] Documents Loaded : {len(documents)}")

# =====================================================
# Insert Graph
# =====================================================

count = 0

with driver.session() as session:

    for document in documents:

        mission = document.get("mission", "").strip()

        category = document.get("category", "")

        url = document.get("url", "")

        if not mission:
            continue

        session.run(
            """
            MERGE (m:Mission {name:$mission})
            SET m.category=$category,
                m.url=$url
            """,
            mission=mission,
            category=category,
            url=url
        )

        entities = document.get("entities", [])

        for entity in entities:

            name = entity.get("text", "").strip()

            label = entity.get("label", "ENTITY")

            if not name:
                continue

            if label == "ORG":

                session.run(
                    """
                    MERGE (e:Organization {name:$name})
                    MERGE (m:Mission {name:$mission})
                    MERGE (m)-[:HAS_ORGANIZATION]->(e)
                    """,
                    name=name,
                    mission=mission
                )

            elif label == "PERSON":

                session.run(
                    """
                    MERGE (e:Person {name:$name})
                    MERGE (m:Mission {name:$mission})
                    MERGE (m)-[:HAS_PERSON]->(e)
                    """,
                    name=name,
                    mission=mission
                )

            elif label in ["GPE", "LOC"]:

                session.run(
                    """
                    MERGE (e:Location {name:$name})
                    MERGE (m:Mission {name:$mission})
                    MERGE (m)-[:HAS_LOCATION]->(e)
                    """,
                    name=name,
                    mission=mission
                )

            elif label == "DATE":

                session.run(
                    """
                    MERGE (e:Date {name:$name})
                    MERGE (m:Mission {name:$mission})
                    MERGE (m)-[:HAS_DATE]->(e)
                    """,
                    name=name,
                    mission=mission
                )

            else:

                session.run(
                    """
                    MERGE (e:Entity {name:$name,type:$type})
                    MERGE (m:Mission {name:$mission})
                    MERGE (m)-[:HAS_ENTITY]->(e)
                    """,
                    name=name,
                    type=label,
                    mission=mission
                )

        count += 1

        if count % 100 == 0:

            print(f"{count} documents processed")

# =====================================================
# Summary
# =====================================================

print()
print("=" * 60)
print("GRAPH CREATED SUCCESSFULLY")
print("=" * 60)

with driver.session() as session:

    missions = session.run(
        "MATCH (n:Mission) RETURN count(n) AS c"
    ).single()["c"]

    orgs = session.run(
        "MATCH (n:Organization) RETURN count(n) AS c"
    ).single()["c"]

    persons = session.run(
        "MATCH (n:Person) RETURN count(n) AS c"
    ).single()["c"]

    locations = session.run(
        "MATCH (n:Location) RETURN count(n) AS c"
    ).single()["c"]

    dates = session.run(
        "MATCH (n:Date) RETURN count(n) AS c"
    ).single()["c"]

    entities = session.run(
        "MATCH (n:Entity) RETURN count(n) AS c"
    ).single()["c"]

    relationships = session.run(
        "MATCH ()-[r]->() RETURN count(r) AS c"
    ).single()["c"]

print(f"Missions      : {missions}")
print(f"Organizations : {orgs}")
print(f"Persons       : {persons}")
print(f"Locations     : {locations}")
print(f"Dates         : {dates}")
print(f"Other Entities: {entities}")
print(f"Relationships : {relationships}")

driver.close()

print()
print("=" * 60)
print("UPLOAD TO NEO4J COMPLETED")
print("=" * 60)