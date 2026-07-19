import json

from scrapers.url_loader import (
    load_urls,
    get_mission_urls
)

from scrapers.mission_scraper import scrape_mission

from scrapers.entity_extractor import extract_custom_entities

from processors.entity_resolver import resolve_entities
from processors.entity_classifier import classify_entities

from scrapers.relationship_builder import create_relationships
from scrapers.document_classifier import classify_document


structured_data = []

# ==========================================================
# Load URLs
# ==========================================================

all_urls = load_urls("data/isro_links.txt")

MISSION_URLS = get_mission_urls(all_urls)

print(f"\nFound {len(MISSION_URLS)} mission URLs")


# ==========================================================
# Process Each Mission
# ==========================================================

for url in MISSION_URLS:

    mission = scrape_mission(url)

    if not mission:
        continue

    search_text = (
        mission["title"]
        + " "
        + mission["content"][:2000]
    )

    # ------------------------------------------------------
    # Entity Pipeline
    # ------------------------------------------------------

    entities = extract_custom_entities(search_text)

    entities = resolve_entities(entities)

    entities = classify_entities(entities)

    # ------------------------------------------------------
    # Extract Launch Vehicles
    # ------------------------------------------------------

    launch_vehicles = [

        entity["name"]

        for entity in entities

        if entity["type"] in (

            "LAUNCH_VEHICLE",

            "ROCKET_VARIANT"

        )

    ]

    # ------------------------------------------------------
    # Extract Organizations
    # ------------------------------------------------------

    organizations = [

        entity["name"]

        for entity in entities

        if entity["type"] == "ORGANIZATION"

    ]

    # ------------------------------------------------------
    # Document Type
    # ------------------------------------------------------

    document_type = classify_document(
        mission["title"]
    )

    # ------------------------------------------------------
    # Build Record
    # ------------------------------------------------------

    record = {

        "title": mission["title"],

        "document_type": document_type,

        "content": mission["content"],

        "entities": entities,

        "launch_vehicles": launch_vehicles,

        "organizations": organizations,

        "url": mission["url"],

        "source": "ISRO"

    }

    structured_data.append(record)


# ==========================================================
# Save JSON
# ==========================================================

output_file = "data/raw/isro/structured_missions.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        structured_data,
        f,
        indent=4,
        ensure_ascii=False
    )

print(f"\nSaved {len(structured_data)} records")
print(f"Output File : {output_file}")


# ==========================================================
# Print Extracted Entities
# ==========================================================

print("\n" + "=" * 80)
print("EXTRACTED ENTITIES")
print("=" * 80)

for record in structured_data:

    print(f"\nDocument : {record['title']}")

    print("-" * 80)

    for entity in record["entities"]:

        print(

            f"{entity['type']:<20}"

            f"{entity['name']}"

        )


# ==========================================================
# Build Relationships
# ==========================================================

all_relationships = []

for record in structured_data:

    relationships = create_relationships(record)

    all_relationships.extend(
        relationships
    )


# ==========================================================
# Print Relationships
# ==========================================================

# print("\n" + "=" * 80)
# print("KNOWLEDGE GRAPH RELATIONSHIPS")
# print("=" * 80)

# for relationship in all_relationships:

#     print(relationship)

# print("\nTotal Relationships :", len(all_relationships))