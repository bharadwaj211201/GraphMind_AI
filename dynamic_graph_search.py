from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "graphmind123")
)

def run_cypher(query):

    with driver.session() as session:

        result = session.run(query)

        records = []

        for record in result:
            records.append(dict(record))

        return records