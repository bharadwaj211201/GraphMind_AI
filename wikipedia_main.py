"""
==========================================================
Wikipedia Data Collection Pipeline
Knowledge Graph Project

Purpose
-------
Collect Wikipedia articles for all ISRO missions,
extract entities, and save structured JSON files.

Pipeline
--------
MISSIONS
    ↓
Wikipedia Search
    ↓
Wikipedia Scraper
    ↓
Entity Extractor
    ↓
wikipedia_pages.json

    ↓

wikipedia_entities.json

Author : Bharadwaj
==========================================================
"""

import os
import json
from datetime import datetime

from scrapers.domain_entities import (
    MISSIONS,
    SATELLITES,
    SPACECRAFT,
    LAUNCH_VEHICLES
)
from scrapers.wiki_loader import search_multiple
from scrapers.wikipedia_scraper import scrape_wikipedia
from scrapers.entity_extractor import extract_custom_entities


# ==========================================================
# Output Configuration
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "wikipedia"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

PAGES_FILE = os.path.join(
    OUTPUT_DIR,
    "wikipedia_pages.json"
)

ENTITY_FILE = os.path.join(
    OUTPUT_DIR,
    "wikipedia_entities.json"
)


# ==========================================================
# Statistics
# ==========================================================

stats = {

    "missions": 0,

    "pages_found": 0,

    "pages_failed": 0,

    "entities": 0,

    "start_time": datetime.now()

}


# ==========================================================
# Helper Functions
# ==========================================================

def save_json(data, filename):
    """
    Save JSON with pretty formatting.
    """

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def print_header():

    print()

    print("=" * 70)

    print("Wikipedia Knowledge Collection")

    print("=" * 70)

    print(f"Total Missions : {len(MISSIONS)}")

    print()


def print_summary():

    end = datetime.now()

    duration = end - stats["start_time"]

    print()

    print("=" * 70)

    print("Collection Summary")

    print("=" * 70)

    print(f"Missions           : {stats['missions']}")

    print(f"Pages Collected    : {stats['pages_found']}")

    print(f"Pages Failed       : {stats['pages_failed']}")

    print(f"Entities Extracted : {stats['entities']}")

    print(f"Execution Time     : {duration}")

    print("=" * 70)

# ==========================================================
# Main Collection Pipeline
# ==========================================================

def collect_wikipedia_data():
    """
    Collect Wikipedia articles for all ISRO missions.

    Returns
    -------
    tuple
        (
            wikipedia_pages,
            wikipedia_entities
        )
    """

    wikipedia_pages = []
    wikipedia_entities = []

    print("Searching Wikipedia...\n")

    knowledge_items = (
        MISSIONS +
        SATELLITES +
        SPACECRAFT +
        LAUNCH_VEHICLES
    )

    mission_urls = search_multiple(knowledge_items)

    stats["missions"] = len(MISSIONS)

    print("\nStarting Wikipedia scraping...\n")

    for index, mission in enumerate(MISSIONS, start=1):

        print("-" * 70)
        print(f"[{index}/{len(MISSIONS)}] {mission}")

        url = mission_urls.get(mission)

        if not url:

            print("No Wikipedia page found.\n")

            stats["pages_failed"] += 1

            continue

        page = scrape_wikipedia(url)

        if not page:

            print("Unable to scrape page.\n")

            stats["pages_failed"] += 1

            continue

        title = page.get("title", "")
        content = page.get("content", "")
        page_url = page.get("url", url)

        if not content.strip():

            print("Empty article.\n")

            stats["pages_failed"] += 1

            continue

        print(f"Downloaded : {title}")

        # --------------------------------------------------
        # Entity Extraction
        # --------------------------------------------------

        entities = extract_custom_entities(content)

        stats["entities"] += len(entities)

        print(f"Entities : {len(entities)}")

        # --------------------------------------------------
        # Store Wikipedia Page
        # --------------------------------------------------

        wikipedia_pages.append(

            {

                "mission": mission,

                "title": title,

                "url": page_url,

                "source": "Wikipedia",

                "content": content,

                "content_length": len(content),

                "entity_count": len(entities)

            }

        )

        # --------------------------------------------------
        # Store Extracted Entities
        # --------------------------------------------------

        wikipedia_entities.append(

            {

                "mission": mission,

                "title": title,

                "url": page_url,

                "entities": [

                    {

                        "name": entity,

                        "type": entity_type

                    }

                    for entity, entity_type in entities

                ]

            }

        )

        stats["pages_found"] += 1

        print("Completed.\n")

    return wikipedia_pages, wikipedia_entities

# ==========================================================
# Save Output Files
# ==========================================================

def save_outputs(wikipedia_pages, wikipedia_entities):
    """
    Save collected Wikipedia data to JSON files.
    """

    print("\nSaving output files...\n")

    save_json(
        wikipedia_pages,
        PAGES_FILE
    )

    save_json(
        wikipedia_entities,
        ENTITY_FILE
    )

    print(f"Saved : {PAGES_FILE}")
    print(f"Saved : {ENTITY_FILE}")


# ==========================================================
# Verify Results
# ==========================================================

def verify_outputs(wikipedia_pages, wikipedia_entities):
    """
    Perform basic validation on generated outputs.
    """

    print("\nVerifying outputs...\n")

    assert len(wikipedia_pages) == len(
        wikipedia_entities
    ), "Mismatch between pages and entities."

    for page in wikipedia_pages:

        if "content" not in page:
            raise ValueError(
                "Wikipedia page missing content."
            )

        if len(page["content"].strip()) == 0:
            raise ValueError(
                "Wikipedia page has empty content."
            )

    print("Verification successful.\n")


# ==========================================================
# Main
# ==========================================================

def main():

    print_header()

    wikipedia_pages, wikipedia_entities = (
        collect_wikipedia_data()
    )

    save_outputs(
        wikipedia_pages,
        wikipedia_entities
    )

    verify_outputs(
        wikipedia_pages,
        wikipedia_entities
    )

    print_summary()


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()