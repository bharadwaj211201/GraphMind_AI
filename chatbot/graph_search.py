from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "graphmind123")
)


def search_graph(mission, intent):

    with driver.session() as session:

        if intent == "organization":

            query = """
            MATCH (m:Mission)-[:HAS_ORGANIZATION]->(o)
            WHERE toLower(m.name) CONTAINS toLower($mission)
            RETURN m.name AS Mission,
                   collect(DISTINCT o.name) AS Result
            LIMIT 5
            """

        elif intent == "person":

            query = """
            MATCH (m:Mission)-[:HAS_PERSON]->(p)
            WHERE toLower(m.name) CONTAINS toLower($mission)
            RETURN m.name AS Mission,
                   collect(DISTINCT p.name) AS Result
            LIMIT 5
            """

        elif intent == "location":

            query = """
            MATCH (m:Mission)-[:HAS_LOCATION]->(l)
            WHERE toLower(m.name) CONTAINS toLower($mission)
            RETURN m.name AS Mission,
                   collect(DISTINCT l.name) AS Result
            LIMIT 5
            """

        elif intent == "date":

            query = """
            MATCH (m:Mission)-[:HAS_DATE]->(d)
            WHERE toLower(m.name) CONTAINS toLower($mission)
            RETURN m.name AS Mission,
                   collect(DISTINCT d.name) AS Result
            LIMIT 5
            """

        else:

            query = """
            MATCH (m:Mission)
            WHERE toLower(m.name) CONTAINS toLower($mission)

            OPTIONAL MATCH (m)-[:HAS_ORGANIZATION]->(o)
            OPTIONAL MATCH (m)-[:HAS_PERSON]->(p)
            OPTIONAL MATCH (m)-[:HAS_LOCATION]->(l)
            OPTIONAL MATCH (m)-[:HAS_DATE]->(d)

            RETURN
            m.name AS Mission,
            collect(DISTINCT o.name) AS Organizations,
            collect(DISTINCT p.name) AS People,
            collect(DISTINCT l.name) AS Locations,
            collect(DISTINCT d.name) AS Dates
            LIMIT 5
            """

        result = session.run(query, mission=mission)

        return [dict(r) for r in result]