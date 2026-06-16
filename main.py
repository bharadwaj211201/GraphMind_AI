import json

from scrapers.url_loader import (
    load_urls,
    get_mission_urls
)
from scrapers.mission_scraper import scrape_mission
from scrapers.entity_extractor import (
    extract_custom_entities,
    extract_launch_vehicle,
    extract_organizations
)
from scrapers.relationship_builder import create_relationships

structured_data = []

all_urls = load_urls("data/isro_links.txt")

MISSION_URLS = get_mission_urls(all_urls)

print(f"Found {len(MISSION_URLS)} mission urls")

print("\nMission URLs Found:\n")

for url in MISSION_URLS:
    print(url)

for url in MISSION_URLS:

    mission = scrape_mission(url)

    if mission:
        
        vehicles = extract_launch_vehicle(
            mission["title"] + " " + 
            mission["content"][:2000]
        )

        orgs = extract_organizations(
            mission["title"] + " " +
            mission["content"][:2000]
        )

        custom_entities = extract_custom_entities(
            mission["title"] + " " +
            mission["content"][:2000]
        )

        record = {
            "mission_name": mission["title"],
            "launch_vehicles": vehicles,
            "organizations": orgs,
            "custom_entities": custom_entities,
            "url": mission["url"]
        }

        structured_data.append(record)

with open(
    "output/structured_missions.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        structured_data,
        f,
        indent=4,
        ensure_ascii=False
    )

print("Saved", len(structured_data), "missions")

print("\n" + "="*60)
print("CUSTOM ENTITIES")
print("="*60)

for r in structured_data:

    print("\nMission:", r["mission_name"])

    for entity in r["custom_entities"]:
        print(entity)

all_relationships = []

for record in structured_data:
    rels = create_relationships(record)

    all_relationships.extend(rels)

print("\n" + "="*60)
print("RELATIONSHIPS")
print("="*60)

for r in all_relationships:
    print(r)