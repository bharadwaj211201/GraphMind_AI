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

<<<<<<< HEAD
=======
from scrapers.document_classifier import classify_document

>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e
structured_data = []

all_urls = load_urls("data/isro_links.txt")

MISSION_URLS = get_mission_urls(all_urls)

print(f"Found {len(MISSION_URLS)} mission urls")

print("\nMission URLs Found:\n")

<<<<<<< HEAD
for url in MISSION_URLS:
    print(url)
=======
# for url in MISSION_URLS:
#     print(url)
>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e

for url in MISSION_URLS:

    mission = scrape_mission(url)

    if mission:
        
<<<<<<< HEAD
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
=======
        search_text = (
            mission['title'] +
            " " +
            mission["content"][:2000]
        )

        vehicles = extract_launch_vehicle(
            search_text
        )

        orgs = extract_organizations(
            search_text
        )

        custom_entities = extract_custom_entities(
            search_text
        )

        doc_type = classify_document(
            mission["title"]
>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e
        )

        record = {
            "mission_name": mission["title"],
<<<<<<< HEAD
            "launch_vehicles": vehicles,
            "organizations": orgs,
            "custom_entities": custom_entities,
            "url": mission["url"]
=======

            "document_type": doc_type,

            "content": mission["content"],

            "launch_vehicles": vehicles,

            "organizations": orgs,

            "custom_entities": custom_entities,

            "url": mission["url"],

            "source": "ISRO"
>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e
        }

        structured_data.append(record)

with open(
<<<<<<< HEAD
    "output/structured_missions.json",
=======
    "data/raw/isro/structured_missions.json",
>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e
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