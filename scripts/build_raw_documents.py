import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scrapers.entity_extractor import (
    extract_launch_vehicles,
    extract_organizations,
    extract_custom_entities
)

from scrapers.document_classifier import classify_document

raw_documents = []


def standardize_document(
    mission_name,
    content,
    url="",
    source="UNKNOWN"
):

    search_text = mission_name + " " + content[:2000]

    vehicles = extract_launch_vehicles(search_text)


    organizations = extract_organizations(search_text)

    custom_entities = extract_custom_entities(search_text)

    if source == "PDF":
        document_type = "PDF"

    elif source == "WIKIPEDIA":
        document_type = "WIKIPEDIA"

    else:
        document_type = classify_document(
            mission_name
        )

    return {
        "mission_name": mission_name,
        "document_type": document_type,
        "content": content,
        "launch_vehicles": vehicles,
        "organizations": organizations,
        "custom_entities": custom_entities,
        "url": url,
        "source": source
    }


# =====================================================
# ISRO DOCUMENTS
# =====================================================

with open(
    "data/raw/isro/structured_missions.json",
    "r",
    encoding="utf-8"
) as f:

    isro_docs = json.load(f)

for doc in isro_docs:

    raw_documents.append(doc)


# =====================================================
# PDF DOCUMENTS
# =====================================================

with open(
    "data/raw/pdfs/pdf_documents.json",
    "r",
    encoding="utf-8"
) as f:

    pdf_docs = json.load(f)

for doc in pdf_docs:

    raw_documents.append(

        standardize_document(

            mission_name=doc.get(
                "title",
                "Unknown PDF"
            ),

            content=doc.get(
                "content",
                ""
            ),

            source="PDF"
        )
    )


# =====================================================
# WIKIPEDIA DOCUMENTS
# =====================================================

try:

    with open(
        "data/raw/wikipedia/wikipedia_data.json",
        "r",
        encoding="utf-8"
    ) as f:

        wiki_docs = json.load(f)

    for doc in wiki_docs:

        raw_documents.append(

            standardize_document(

                mission_name=doc.get(
                    "title",
                    "Wikipedia Page"
                ),

                content=doc.get(
                    "content",
                    ""
                ),

                url=doc.get(
                    "url",
                    ""
                ),

                source="WIKIPEDIA"
            )
        )

except FileNotFoundError:

    print("Wikipedia data not found. Skipping...")


# =====================================================
# REMOVE DUPLICATES
# =====================================================

unique_documents = []

seen = set()

for doc in raw_documents:

    key = (

        doc["mission_name"].lower(),

        doc["source"],

        doc["url"]
    )

    if key not in seen:

        seen.add(key)

        unique_documents.append(doc)


# =====================================================
# SAVE
# =====================================================

with open(
    "data/raw/raw_documents.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        unique_documents,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\n" + "=" * 60)

print("RAW DOCUMENT BUILD COMPLETED")

print("=" * 60)

print("ISRO Documents      :", len(isro_docs))
print("PDF Documents       :", len(pdf_docs))

try:
    print("Wikipedia Documents :", len(wiki_docs))
except NameError:
    print("Wikipedia Documents : 0")

print("-" * 60)

print("Total Documents     :", len(unique_documents))