from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "graphmind123")
)


def execute_cypher(query):

    with driver.session() as session:

        result = session.run(query)

        return [dict(record) for record in result]