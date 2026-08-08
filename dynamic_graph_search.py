from neo4j import GraphDatabase
from chatbot.config import NEO4J_URI, USERNAME, PASSWORD

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(USERNAME, PASSWORD)
)


def run_cypher(query):

    with driver.session() as session:

        result = session.run(query)

        records = []

        for record in result:
            records.append(dict(record))

        return records