import json
from pathlib import Path
from neo4j import GraphDatabase
from chatbot.config import NEO4J_URI, USERNAME, PASSWORD

try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(USERNAME, PASSWORD)
    )
except Exception:
    driver = None

KB_FILE = Path(__file__).resolve().parent.parent / "data" / "merged" / "final_knowledge_base.json"


def get_in_memory_dashboard_data():
    if not KB_FILE.exists():
        return {
            "missions": 0, "organizations": 0, "people": 0,
            "locations": 0, "dates": 0, "mission_list": [],
            "organization_list": [], "is_neo4j": False
        }

    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            missions_data = json.load(f)
    except Exception:
        missions_data = []

    missions = set()
    organizations = set()
    people = set()
    locations = set()
    dates = set()

    mission_list = []
    org_list = []

    for item in missions_data:
        m_title = item.get("title")
        if m_title:
            missions.add(m_title)
            if len(mission_list) < 10:
                mission_list.append({"Mission": m_title})

        for ent in item.get("entities", []):
            e_name = ent.get("name")
            e_type = ent.get("type", "")
            if not e_name:
                continue

            if e_type == "ORGANIZATION":
                organizations.add(e_name)
                if len(org_list) < 10 and {"Organization": e_name} not in org_list:
                    org_list.append({"Organization": e_name})
            elif e_type in ("PERSON", "SCIENTIST", "ASTRONAUT"):
                people.add(e_name)
            elif e_type in ("LOCATION", "CITY", "STATE", "COUNTRY", "SPACEPORT"):
                locations.add(e_name)
            elif e_type == "DATE":
                dates.add(e_name)

    return {
        "missions": len(missions),
        "organizations": len(organizations),
        "people": len(people),
        "locations": len(locations),
        "dates": len(dates),
        "mission_list": mission_list,
        "organization_list": org_list,
        "is_neo4j": False
    }


def get_dashboard_data():
    if driver:
        try:
            with driver.session() as session:
                mission_count = session.run("MATCH (m:Mission) RETURN count(m) AS count").single()["count"]
                org_count = session.run("MATCH (o:Organization) RETURN count(o) AS count").single()["count"]
                person_count = session.run("MATCH (p:Person) RETURN count(p) AS count").single()["count"]
                location_count = session.run("MATCH (l:Location) RETURN count(l) AS count").single()["count"]
                date_count = session.run("MATCH (d:Date) RETURN count(d) AS count").single()["count"]

                missions = session.run("MATCH (m:Mission) RETURN m.name AS Mission LIMIT 10")
                organizations = session.run("MATCH (o:Organization) RETURN o.name AS Organization LIMIT 10")

                return {
                    "missions": mission_count,
                    "organizations": org_count,
                    "people": person_count,
                    "locations": location_count,
                    "dates": date_count,
                    "mission_list": [dict(i) for i in missions],
                    "organization_list": [dict(i) for i in organizations],
                    "is_neo4j": True
                }
        except Exception:
            pass

    # Return local in-memory knowledge base statistics if Neo4j is offline
    return get_in_memory_dashboard_data()