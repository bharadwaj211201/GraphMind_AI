from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError, Neo4jError

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "graphmind123")
)


def execute_cypher(query: str):
    if not query or not query.strip():
        return []

    graph_data = []

    with driver.session() as session:
        try:
            result = session.run(query)

            for record in result:
                record_dict = {}

                for key, value in record.items():
                    if hasattr(value, "labels"):
                        record_dict[key] = {
                            "type": list(value.labels)[0] if value.labels else "Node",
                            "properties": dict(value),
                        }
                    elif hasattr(value, "type"):
                        record_dict[key] = {
                            "relationship": value.type,
                            "properties": dict(value),
                        }
                    else:
                        record_dict[key] = value

                graph_data.append(record_dict)

        except (CypherSyntaxError, Neo4jError, Exception):
            return []

    return graph_data


def close_driver():
    driver.close()