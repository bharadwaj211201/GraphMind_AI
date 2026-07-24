import json
import os
import re
from pathlib import Path
from collections import defaultdict

from scrapers.url_loader import (
    load_urls,
    get_mission_urls
)

from scrapers.mission_scraper import scrape_mission

from scrapers.entity_extractor import extract_custom_entities

from processors.entity_resolver import resolve_entities
from processors.entity_classifier import classify_entities

from scrapers.relationship_builder import print_relationships, build_relationships, print_statistics
from scrapers.document_classifier import classify_document


# ==========================================================
# Pipeline Configuration
# ==========================================================

OUTPUT_DIRECTORY = Path("data/merged")

OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)

MERGED_OUTPUT_FILE = (
    OUTPUT_DIRECTORY /
    "merged_missions.json"
)

ENABLE_WIKIPEDIA = True

ENABLE_PDF = True

PRINT_MERGE_STATISTICS = True

# ==========================================================
# Source Files
# ==========================================================

WEBSITE_OUTPUT = Path(
    "data/raw/isro/structured_missions.json"
)

WIKIPEDIA_OUTPUT = Path(
    "data/raw/wikipedia/wikipedia_pages.json"
)

PDF_OUTPUT = Path(
    "data/raw/pdfs/pdf_documents.json"
)

# ==========================================================
# Mission Name Normalization
# ==========================================================

def normalize_name(name):
    """
    Normalize mission names.

    Examples
    --------
    Aditya-L1

    Aditya L1

    AdityaL1

    ↓

    adityal1
    """

    if not name:
        return ""

    name = name.lower()

    name = re.sub(r"[-_\s]", "", name)

    name = re.sub(r"[^a-z0-9]", "", name)

    return name

# ==========================================================
# Mission Key Extraction
# ==========================================================

MISSION_KEYWORDS = {

    "Aditya-L1": [
        "adityal1",
        "aditya"
    ],

    "AstroSat": [
        "astrosat"
    ],

    "Chandrayaan-1": [
        "chandrayaan1"
    ],

    "Chandrayaan-2": [
        "chandrayaan2"
    ],

    "Chandrayaan-3": [
        "chandrayaan3"
    ],

    "Gaganyaan": [
        "gaganyaan"
    ],

    "SpaDeX": [
        "spadex"
    ],

    "NISAR": [
        "nisar"
    ],

    "Mars Orbiter Mission": [
        "marsorbitermission",
        "marsorbiter",
        "mangalyaan"
    ],

    "PSLV-C59": [
        "pslvc59"
    ],

    "PSLV-C62": [
        "pslvc62"
    ],

    "LVM3": [
        "lvm3"
    ],

    "LVM3-M5": [
        "lvm3m5"
    ],

    "LVM3-M6": [
        "lvm3m6"
    ],

    "GSLV-F11": [
        "gslvf11"
    ],

    "GSLV-F16": [
        "gslvf16"
    ]
}


def extract_mission_key(title):
    """
    Returns:
        canonical_title, mission_key
    """

    if not title:
        return "", ""

    normalized = normalize_name(title)

    for canonical_title, keywords in MISSION_KEYWORDS.items():

        for keyword in keywords:

            if keyword in normalized:

                return (
                    canonical_title,
                    normalize_name(canonical_title)
                )

    return (
        title,
        normalized
    )

# ==========================================================
# Data Containers
# ==========================================================

# Existing ISRO records
structured_data = []

# Individual source records
website_records = []

wikipedia_records = []

pdf_records = []

# Final merged records
merged_records = []


# ==========================================================
# Mission Index
# ==========================================================

"""
Mission Index

Example

mission_index = {

    "adityal1": {

        "title":"Aditya-L1",

        "website":{...},

        "wikipedia":None,

        "pdf":None

    }

}
"""

mission_index = {}


# ==========================================================
# Merge Statistics
# ==========================================================

class MergeStatistics:

    def __init__(self):

        self.website = 0

        self.wikipedia = 0

        self.pdf = 0

        self.merged = 0

    def print_summary(self):

        if not PRINT_MERGE_STATISTICS:

            return

        print()

        print("=" * 70)

        print("MISSION MERGE STATISTICS")

        print("=" * 70)

        print(f"Website Records   : {self.website}")

        print(f"Wikipedia Records : {self.wikipedia}")

        print(f"PDF Records       : {self.pdf}")

        print(f"Merged Missions   : {self.merged}")

        print("=" * 70)


merge_stats = MergeStatistics()

# ==========================================================
# JSON Loader
# ==========================================================

def load_json(file_path):
    """
    Load JSON safely.

    Returns
    -------
    list
    """

    file_path = Path(file_path)

    if not file_path.exists():

        print(f"[WARNING] Missing file : {file_path}")

        return []

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        print(
            f"Loaded {len(data)} records from "
            f"{file_path.name}"
        )

        return data

    except Exception as e:

        print(e)

        return []

# ==========================================================
# Source Registration
# ==========================================================

def register_source(source, record):
    """
    Register one mission record
    into the mission index.
    """

    title = record.get("title", "")

    canonical_title, key = extract_mission_key(title)

    if not key:

        return

    if key not in mission_index:

        mission_index[key] = {

            "title": canonical_title,

            "website": None,

            "wikipedia": None,

            "pdf": None

        }

    mission_index[key][source] = record

    if source == "website":

        merge_stats.website += 1

    elif source == "wikipedia":

        merge_stats.wikipedia += 1

    elif source == "pdf":

        merge_stats.pdf += 1

# ==========================================================
# Load URLs
# ==========================================================

all_urls = load_urls("data/isro_links.txt")

MISSION_URLS = get_mission_urls(all_urls)

print(f"\nFound {len(MISSION_URLS)} mission URLs")


# ==========================================================
# Process Website Missions
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
    # Entity Extraction Pipeline
    # ------------------------------------------------------

    entities = extract_custom_entities(
        search_text
    )

    entities = resolve_entities(
        entities
    )

    entities = classify_entities(
        entities
    )

    # ------------------------------------------------------
    # Launch Vehicles
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
    # Organizations
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
    # Build Website Record
    # ------------------------------------------------------

    website_record = {

        "title": mission["title"],

        "document_type": document_type,

        "content": mission["content"],

        "entities": entities,

        "launch_vehicles": launch_vehicles,

        "organizations": organizations,

        "url": mission["url"],

        "source": "ISRO"

    }

    # ------------------------------------------------------
    # Existing Pipeline
    # ------------------------------------------------------

    structured_data.append(
        website_record
    )

    # ------------------------------------------------------
    # Mission Data Merger Pipeline
    # ------------------------------------------------------

    website_records.append(
        website_record
    )

    register_source(
        "website",
        website_record
    )


print()

print("=" * 70)

print("WEBSITE INGESTION COMPLETE")

print("=" * 70)

print(f"Website Records : {len(website_records)}")

print(f"Mission Index   : {len(mission_index)}")

print("=" * 70)

# ==========================================================
# Process Wikipedia Missions
# ==========================================================

if ENABLE_WIKIPEDIA:

    wikipedia_pages = load_json(
        WIKIPEDIA_OUTPUT
    )

    for mission in wikipedia_pages:

        # -----------------------------
        # Ignore Non-Mission Pages
        # -----------------------------

        _, mission_key = extract_mission_key(
            mission["title"]
        )

        if mission_key not in {normalize_name(name) for name in MISSION_KEYWORDS}:
            continue

        search_text = (

            mission["title"]

            + " "

            + mission["content"][:2000]

        )

        # --------------------------------------------------
        # Entity Extraction
        # --------------------------------------------------

        entities = extract_custom_entities(
            search_text
        )

        entities = resolve_entities(
            entities
        )

        entities = classify_entities(
            entities
        )

        # --------------------------------------------------
        # Launch Vehicles
        # --------------------------------------------------

        launch_vehicles = [

            entity["name"]

            for entity in entities

            if entity["type"] in (

                "LAUNCH_VEHICLE",

                "ROCKET_VARIANT"

            )

        ]

        # --------------------------------------------------
        # Organizations
        # --------------------------------------------------

        organizations = [

            entity["name"]

            for entity in entities

            if entity["type"] == "ORGANIZATION"

        ]

        # --------------------------------------------------
        # Document Type
        # --------------------------------------------------

        document_type = classify_document(
            mission["title"]
        )

        # --------------------------------------------------
        # Wikipedia Record
        # --------------------------------------------------

        wikipedia_record = {

            "title": mission["title"],

            "document_type": document_type,

            "content": mission["content"],

            "entities": entities,

            "launch_vehicles": launch_vehicles,

            "organizations": organizations,

            "url": mission["url"],

            "source": "Wikipedia"

        }

        wikipedia_records.append(
            wikipedia_record
        )

        register_source(
            "wikipedia",
            wikipedia_record
        )

else:

    wikipedia_records = []

# ==========================================================
# Load PDF Dataset
# ==========================================================

if ENABLE_PDF:

    pdf_records = load_json(
        PDF_OUTPUT
    )

else:

    pdf_records = []

print()

print("=" * 70)

print("DATA SOURCES")

print("=" * 70)

print(f"Website Records   : {len(website_records)}")

print(f"Wikipedia Records : {len(wikipedia_records)}")

print(f"PDF Records       : {len(pdf_records)}")

print("=" * 70)

# ==========================================================
# Save Website Structured JSON
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

print()

print("=" * 70)

print("WEBSITE DATA SAVED")

print("=" * 70)

print(f"Records     : {len(structured_data)}")

print(f"Output File : {output_file}")

print("=" * 70)


# ==========================================================
# Print Extracted Entities
# ==========================================================

print()

print("=" * 80)
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

    relationships = build_relationships(record)

    all_relationships.extend(
        relationships
    )


# ============================================================
# Print Relationships
# ============================================================

print_relationships(
    all_relationships
)

print_statistics()

# ==========================================================
# Mission Index Summary
# ==========================================================

print()

print("=" * 80)
print("MISSION INDEX")
print("=" * 80)

for key, mission in mission_index.items():

    print(f"\nMission Key : {key}")

    print(f"Title       : {mission['title']}")

    print(
        f"Website     : "
        f"{'YES' if mission['website'] else 'NO'}"
    )

    print(
        f"Wikipedia   : "
        f"{'YES' if mission['wikipedia'] else 'NO'}"
    )

    print(
        f"PDF         : "
        f"{'YES' if mission['pdf'] else 'NO'}"
    )


# ==========================================================
# Merge Statistics
# ==========================================================

merge_stats.print_summary()


# ==========================================================
# Placeholder for Future Mission Merger
# ==========================================================

"""
Part 2 will begin here.

Pipeline

Website Records
        │

Wikipedia Records
        │

PDF Records
        │

        ▼

Mission Data Merger

        ▼

merged_records

        ▼

merged_missions.json
"""

# ==========================================================
# Stage 1
# Create Empty Mission Records
# ==========================================================

print()

print("=" * 70)
print("STAGE 1 - CREATE EMPTY MERGED RECORDS")
print("=" * 70)

for mission_key, mission in mission_index.items():

    merged_record = {

        # -----------------------------
        # Basic Information
        # -----------------------------

        "title": mission["title"],

        "mission_key": mission_key,

        # -----------------------------
        # Source Tracking
        # -----------------------------

        "sources": [],

        "documents": [],

        # -----------------------------
        # Document Information
        # -----------------------------

        "content": [],

        "urls": [],

        "document_types": [],

        # -----------------------------
        # Knowledge
        # -----------------------------

        "entities": [],

        "relationships": [],

        "launch_vehicles": [],

        "organizations": []

    }

    merged_records.append(merged_record)

print(f"Created {len(merged_records)} empty merged records.")

print()

print("=" * 70)
print("EMPTY MERGED RECORDS")
print("=" * 70)

for record in merged_records[:5]:

    print()

    print(record["title"])

    print(record)

# ==========================================================
# Stage 2
# Merge Website Records
# ==========================================================

print()

print("=" * 70)
print("STAGE 2 - MERGING WEBSITE RECORDS")
print("=" * 70)

website_lookup = {}

for record in website_records:

    _, key = extract_mission_key(record["title"])

    website_lookup[key] = record

for merged in merged_records:

    key = merged["mission_key"]

    if key not in website_lookup:

        continue

    website = website_lookup[key]

    merged["sources"].append(

        website["source"]

    )

    merged["documents"].append(

        website

    )

    merged["content"].append(

        website["content"]

    )

    merged["urls"].append(

        website["url"]

    )

    merged["document_types"].append(

        website["document_type"]

    )

    merged["entities"].extend(

        website["entities"]

    )

    merged["launch_vehicles"].extend(

        website["launch_vehicles"]

    )

    merged["organizations"].extend(

        website["organizations"]

    )

print()

print(f"Merged Website Records : {len(website_lookup)}")

print()

print("=" * 70)
print("WEBSITE MERGE SAMPLE")
print("=" * 70)

for record in merged_records[:3]:

    print()

    print(f"Mission : {record['title']}")

    print(f"Sources : {record['sources']}")

    print(f"Documents : {len(record['documents'])}")

    print(f"Entities : {len(record['entities'])}")

    print(f"Launch Vehicles : {len(record['launch_vehicles'])}")

    print(f"Organizations : {len(record['organizations'])}")

# ==========================================================
# Stage 3
# Merge PDF Records
# ==========================================================

print()

print("=" * 70)
print("STAGE 3 - MERGING PDF RECORDS")
print("=" * 70)

pdf_lookup = {}

for record in pdf_records:

    _, key = extract_mission_key(record["title"])

    pdf_lookup[key] = record

merged_count = 0

for merged in merged_records:

    key = merged["mission_key"]

    if key not in pdf_lookup:

        continue

    pdf = pdf_lookup[key]

    merged_count += 1

    merged["sources"].append(

        pdf["source"]

    )

    merged["documents"].append(

        pdf

    )

    merged["content"].append(

        pdf["content"]

    )

    merged["urls"].append(

        pdf.get(

            "url",

            pdf.get(

                "file_path",

                ""

            )

        )

    )

    merged["document_types"].append(

        pdf.get(

            "document_type",

            "PDF"

        )

    )

    merged["entities"].extend(

        pdf.get(

            "entities",

            []

        )

    )

    merged["launch_vehicles"].extend(

        pdf.get(

            "launch_vehicles",

            []

        )

    )

    merged["organizations"].extend(

        pdf.get(

            "organizations",

            []

        )

    )

print()

print(f"PDF Missions Merged : {merged_count}")

print()

print("=" * 70)
print("PDF MERGE SAMPLE")
print("=" * 70)

for record in merged_records[:5]:

    print()

    print(f"Mission : {record['title']}")

    print(f"Sources : {record['sources']}")

    print(f"Documents : {len(record['documents'])}")

    print(f"Contents : {len(record['content'])}")

# ==========================================================
# Stage 4
# Merge Wikipedia Records
# ==========================================================

print()

print("=" * 70)
print("STAGE 4 - MERGING WIKIPEDIA RECORDS")
print("=" * 70)

wikipedia_lookup = {}

for record in wikipedia_records:

    _, key = extract_mission_key(
        record["title"]
    )

    wikipedia_lookup[key] = record

merged_count = 0

for merged in merged_records:

    key = merged["mission_key"]

    if key not in wikipedia_lookup:

        continue

    wikipedia = wikipedia_lookup[key]

    merged_count += 1

    merged["sources"].append(

        wikipedia["source"]

    )

    merged["documents"].append(

        wikipedia

    )

    merged["content"].append(

        wikipedia["content"]

    )

    merged["urls"].append(

        wikipedia["url"]

    )

    merged["document_types"].append(

        wikipedia["document_type"]

    )

    merged["entities"].extend(

        wikipedia["entities"]

    )

    merged["launch_vehicles"].extend(

        wikipedia["launch_vehicles"]

    )

    merged["organizations"].extend(

        wikipedia["organizations"]

    )

print()

print(f"Wikipedia Missions Merged : {merged_count}")

print()

print("=" * 70)
print("WIKIPEDIA MERGE SAMPLE")
print("=" * 70)

for record in merged_records[:5]:

    print()

    print(f"Mission : {record['title']}")

    print(f"Sources : {record['sources']}")

    print(f"Documents : {len(record['documents'])}")

    print(f"Contents : {len(record['content'])}")

# ==========================================================
# Stage 5
# Remove Duplicate Entities
# ==========================================================

print()

print("=" * 70)
print("STAGE 5 - DEDUPLICATING ENTITIES")
print("=" * 70)

for merged in merged_records:

    unique_entities = {}

    for entity in merged["entities"]:

        name = entity.get("name", "").strip()

        entity_type = entity.get("type", "")

        if not name:

            continue

        key = (

            normalize_name(name),

            entity_type

        )

        if key not in unique_entities:
            unique_entities[key] = {
                "name": name,
                "type": entity_type,
                "aliases": [name],
                "sources": list(merged["sources"])
            }
        else:
            existing = unique_entities[key]
            if name not in existing["aliases"]:
                existing["aliases"].append(name)
            for source in merged["sources"]:
                if source not in existing["sources"]:
                    existing["sources"].append(source)

    merged["entities"] = list(

        unique_entities.values()
    )

print()

print("Entity Deduplication Completed.")

print()

print("=" * 70)
print("ENTITY DEDUPLICATION SAMPLE")
print("=" * 70)

for record in merged_records[:5]:

    print()

    print(record["title"])

    print(

        "Unique Entities :",

        len(record["entities"])

    )

# ==========================================================
# Stage 6A
# Relationship Mapping Configuration
# ==========================================================

print()
print("=" * 70)
print("STAGE 6A - RELATIONSHIP MAPPING")
print("=" * 70)

RELATIONSHIP_MAP = {

    # -----------------------------------------------------
    # Mission
    # -----------------------------------------------------
    "MISSION": {
        "relationship": "MISSION",
        "node_label": "Mission"
    },

    # -----------------------------------------------------
    # Organizations
    # -----------------------------------------------------
    "ORGANIZATION": {
        "relationship": "INVOLVES",
        "node_label": "Organization"
    },

    "AGENCY": {
        "relationship": "PARTNERS_WITH",
        "node_label": "Agency"
    },

    # -----------------------------------------------------
    # Launch Vehicles
    # -----------------------------------------------------
    "LAUNCH_VEHICLE": {
        "relationship": "USES",
        "node_label": "LaunchVehicle"
    },

    "ROCKET_VARIANT": {
        "relationship": "USES",
        "node_label": "RocketVariant"
    },

    # -----------------------------------------------------
    # Space Objects
    # -----------------------------------------------------
    "SPACECRAFT": {
        "relationship": "CARRIES",
        "node_label": "Spacecraft"
    },

    "SATELLITE": {
        "relationship": "DEPLOYS",
        "node_label": "Satellite"
    },

    "PAYLOAD": {
        "relationship": "TRANSPORTS",
        "node_label": "Payload"
    },

    # -----------------------------------------------------
    # People
    # -----------------------------------------------------
    "PERSON": {
        "relationship": "DEVELOPED_BY",
        "node_label": "Person"
    },

    "SCIENTIST": {
        "relationship": "DEVELOPED_BY",
        "node_label": "Scientist"
    },

    # -----------------------------------------------------
    # Geography
    # -----------------------------------------------------
    "LOCATION": {
        "relationship": "LAUNCHED_FROM",
        "node_label": "Location"
    },

    "COUNTRY": {
        "relationship": "COLLABORATES_WITH",
        "node_label": "Country"
    }

}

print()
print(f"Relationship Types Loaded : {len(RELATIONSHIP_MAP)}")
print()

for entity_type, config in RELATIONSHIP_MAP.items():

    print(
        f"{entity_type:<20} "
        f"Relationship: {config['relationship']:<18} "
        f"Node Label: {config['node_label']}"
    )

# ==========================================================
# Stage 6B
# Mission → Entity Relationship Builder
# ==========================================================

print()
print("=" * 70)
print("STAGE 6B - BUILDING MISSION → ENTITY RELATIONSHIPS")
print("=" * 70)

GRAPH_ENTITY_TYPES = {

    "MISSION",

    "ORGANIZATION",

    "AGENCY",

    "LAUNCH_VEHICLE",

    "ROCKET_VARIANT",

    "SPACECRAFT",

    "SATELLITE",

    "PAYLOAD",

    "PERSON",

    "SCIENTIST",

    "LOCATION",

    "COUNTRY"

}

relationship_count = 0

# Global relationship repository
all_relationships = []

for mission in merged_records:

    mission_name = mission["title"]

    mission.setdefault("relationships", [])

    existing_relationships = set()

    for entity in mission["entities"]:

        entity_name = entity.get("name", "").strip()
        entity_type = entity.get("type", "").strip()

        if not entity_name:
            continue

        if not entity_type:
            continue

        if entity_type not in GRAPH_ENTITY_TYPES:
            continue

        if entity_type not in RELATIONSHIP_MAP:
            continue

        # Skip self-loop
        if normalize_name(entity_name) == normalize_name(mission_name):
            continue

        config = RELATIONSHIP_MAP[entity_type]

        relationship_key = (

            normalize_name(mission_name),

            config["relationship"],

            normalize_name(entity_name)

        )

        if relationship_key in existing_relationships:
            continue

        existing_relationships.add(relationship_key)

        relationship = {

            "relationship_id": f"REL_{relationship_count + 1:06d}",

            "source": mission_name,

            "source_type": "MISSION",

            "source_label": "Mission",

            "target": entity_name,

            "target_type": entity_type,

            "target_label": config["node_label"],

            "relationship": config["relationship"],

            "evidence": sorted(list(set(entity.get("sources", [])))),

            "confidence": 1.0

        }

        mission["relationships"].append(relationship)

        all_relationships.append(relationship)

        relationship_count += 1


print()
print(f"Relationships Created : {relationship_count}")
print(f"Global Relationships  : {len(all_relationships)}")

print()

for mission in merged_records[:3]:

    print(f"\nMission : {mission['title']}")

    if not mission["relationships"]:
        print("  No Relationships")
        continue

    for rel in mission["relationships"][:5]:

        print(
            f"  {rel['source']} "
            f"--[{rel['relationship']}]--> "
            f"{rel['target']}"
        )

# ==========================================================
# Stage 7
# Save Final Knowledge Base
# ==========================================================

print()
print("=" * 70)
print("STAGE 7 - SAVING FINAL KNOWLEDGE BASE")
print("=" * 70)

import os
import json

# ----------------------------------------------------------
# Create merged directory if it doesn't exist
# ----------------------------------------------------------

os.makedirs("data/merged", exist_ok=True)

# ----------------------------------------------------------
# Sort missions alphabetically
# ----------------------------------------------------------

merged_records = sorted(
    merged_records,
    key=lambda mission: mission.get("title", "")
)

# ----------------------------------------------------------
# Save Final Knowledge Base
# ----------------------------------------------------------

output_file = "data/merged/final_knowledge_base.json"

with open(output_file, "w", encoding="utf-8") as file:

    json.dump(
        merged_records,
        file,
        indent=4,
        ensure_ascii=False
    )

print()

print(f"Knowledge Records : {len(merged_records)}")

print(f"Saved To          : {output_file}")

print()

print("Sample Missions")

print("-" * 70)

for mission in merged_records[:3]:

    print()

    print(f"Mission          : {mission.get('title')}")

    print(f"Entities         : {len(mission.get('entities', []))}")

    print(f"Relationships    : {len(mission.get('relationships', []))}")

    print(f"Documents        : {len(mission.get('documents', []))}")

    print(f"Sources          : {len(mission.get('sources', []))}")

# ==========================================================
# Print Relationships (Optional)
# ==========================================================

# print()
# print("=" * 80)
# print("KNOWLEDGE GRAPH RELATIONSHIPS")
# print("=" * 80)
#
# for relationship in all_relationships:
#
#     print(relationship)
#
# print("\nTotal Relationships :", len(all_relationships))