from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "graphmind123")
)


def get_dashboard_data():

    with driver.session() as session:

        mission_count = session.run(
            "MATCH (m:Mission) RETURN count(m) AS count"
        ).single()["count"]

        org_count = session.run(
            "MATCH (o:Organization) RETURN count(o) AS count"
        ).single()["count"]

        person_count = session.run(
            "MATCH (p:Person) RETURN count(p) AS count"
        ).single()["count"]

        location_count = session.run(
            "MATCH (l:Location) RETURN count(l) AS count"
        ).single()["count"]

        date_count = session.run(
            "MATCH (d:Date) RETURN count(d) AS count"
        ).single()["count"]

        missions = session.run("""
        MATCH (m:Mission)
        RETURN m.name AS Mission
        LIMIT 10
        """)

        organizations = session.run("""
        MATCH (o:Organization)
        RETURN o.name AS Organization
        LIMIT 10
        """)

        return {
            "missions": mission_count,
            "organizations": org_count,
            "people": person_count,
            "locations": location_count,
            "dates": date_count,
            "mission_list": [dict(i) for i in missions],
            "organization_list": [dict(i) for i in organizations]
        }