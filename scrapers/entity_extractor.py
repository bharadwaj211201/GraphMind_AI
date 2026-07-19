"""
==========================================================
Entity Extractor
Knowledge Graph Project

Purpose:
    Extract entities from mission documents using
    1. Dictionary Matching
    2. Regex Matching
    3. spaCy Named Entity Recognition

Author: Bharadwaj
==========================================================
"""

import re
import spacy

from scrapers.domain_entities import *


# ==========================================================
# Load spaCy
# ==========================================================

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found.\n"
        "Run:\n"
        "python -m spacy download en_core_web_sm"
    )


# ==========================================================
# Noise Words
# ==========================================================

STOP_WORDS = {

    "home",
    "mission home",
    "home /",
    "page",
    "more details",
    "gallery",
    "download",
    "pdf",
    "format",
    "file",
    "file size",
    "size",
    "kb",
    "mb",
    "tb",
    "image",
    "images",
    "click",
    "click here",
    "press release",
    "announcement",
    "news",
    "copyright",

    "ao",
    "cme",
    "doi",

    "http",
    "https",
    "www"

}


# ==========================================================
# Regular Expressions
# ==========================================================

ROCKET_PATTERNS = [

    r"\bPSLV-[A-Z]?\d+\b",
    r"\bGSLV-[A-Z]?\d+\b",
    r"\bSSLV-[A-Z]?\d+\b",
    r"\bLVM3-[A-Z]?\d+\b"

]

PAYLOAD_PATTERNS = [

    r"\bCHACE-\d+\b",
    r"\bRAMBHA(?:-[A-Z]+)?\b",
    r"\bHEL1OS\b",
    r"\bVELC\b",
    r"\bSUIT\b",
    r"\bASPEX\b",
    r"\bPAPA\b",
    r"\bMAG\b",
    r"\bSoLEXS\b",
    r"\bDFSAR\b",
    r"\bOHRC\b",
    r"\bCLASS\b",
    r"\bIIRS\b",
    r"\bChaSTE\b",
    r"\bILSA\b",
    r"\bSHAPE\b",
    r"\bUVIT\b",
    r"\bCZTI\b",
    r"\bLAXPC\b",
    r"\bSXT\b",
    r"\bPOLIX\b",
    r"\bXSPECT\b"

]

SATELLITE_PATTERNS = [

    r"\bGSAT-\d+[A-Z]?\b",
    r"\bINSAT-\d+[A-Z]?\b",
    r"\bIRNSS-\d+[A-Z]?\b",
    r"\bEOS-\d+\b",
    r"\bRISAT-\d+[A-Z]?\b",
    r"\bCartosat-\d+[A-Z]?\b",
    r"\bResourcesat-\d+[A-Z]?\b",
    r"\bOceansat-\d+[A-Z]?\b"

]


# ==========================================================
# Helper Functions
# ==========================================================

def clean_text(text: str) -> str:
    """
    Basic text cleaning.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize(text: str) -> str:
    """
    Normalize text for comparison.
    """

    text = clean_text(text)

    return text.lower()


def valid_entity(name):

    if not name:
        return False

    name = clean_text(name)

    if len(name) < 2:
        return False

    lower = name.lower()

    if lower in STOP_WORDS:
        return False

    if lower.startswith("home"):
        return False

    if lower.startswith("mission home"):
        return False

    if "home /" in lower:
        return False

    if "download" in lower:
        return False

    if "gallery" in lower:
        return False

    if "more details" in lower:
        return False

    if "file size" in lower:
        return False

    if "format" == lower:
        return False

    if lower in {"kb", "mb", "tb"}:
        return False

    if re.fullmatch(r"\d+", name):
        return False

    if name.startswith("http"):
        return False

    if len(name.split()) > 8:
        return False

    return True


# ==========================================================
# Dictionary Lookup
# ==========================================================

def dictionary_lookup(text):
    """
    Dictionary based entity extraction.

    Returns:
        [
            ("ISRO","ORGANIZATION"),
            ("Chandrayaan-3","MISSION")
        ]
    """

    entities = []

    lower_text = normalize(text)

    for entity_type, values in ENTITY_LOOKUP.items():

        for value in values:

            pattern = r"\b" + re.escape(value.lower()) + r"\b"

            if re.search(pattern, lower_text):

                entities.append(

                    (
                        value,
                        entity_type
                    )

                )

    return entities


# ==========================================================
# Regex Extraction Helper
# ==========================================================

def extract_by_patterns(text, patterns, entity_type):
    """
    Generic regex extractor.
    """

    entities = []

    for pattern in patterns:

        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for match in matches:

            entities.append(

                (
                    match,
                    entity_type
                )

            )

    return entities

# ==========================================================
# Regex Extraction
# ==========================================================

def regex_lookup(text):
    """
    Extract entities using predefined regex patterns.

    Returns
    -------
    [
        ("PSLV-C62","ROCKET_VARIANT"),
        ("VELC","PAYLOAD")
    ]
    """

    entities = []

    entities.extend(

        extract_by_patterns(
            text,
            ROCKET_PATTERNS,
            "ROCKET_VARIANT"
        )

    )

    entities.extend(

        extract_by_patterns(
            text,
            PAYLOAD_PATTERNS,
            "PAYLOAD"
        )

    )

    entities.extend(

        extract_by_patterns(
            text,
            SATELLITE_PATTERNS,
            "SATELLITE"
        )

    )

    return entities


# ==========================================================
# spaCy Extraction
# ==========================================================

def spacy_lookup(text):
    """
    Named Entity Recognition using spaCy.

    Used only when dictionary extraction
    misses an entity.
    """

    entities = []

    doc = nlp(text)

    for ent in doc.ents:

        value = clean_text(ent.text)

        if not valid_entity(value):
            continue

        label = ent.label_

        if label == "ORG":

            if len(value.split()) > 6:
                continue
            if value.lower().startswith("home"):
                continue
            if "/" in value:
                continue

            entities.append((value, "ORGANIZATION"))

        elif label == "PERSON":

            if len(value.split()) > 4:
                continue

            entities.append(

                (
                    value,
                    "PERSON"
                )

            )

        elif label in {

            "GPE",
            "LOC"

        }:
            if len(value.split()) > 4:
                continue

            entities.append(

                (
                    value,
                    "LOCATION"
                )

            )

    return entities


# ==========================================================
# Entity Validation
# ==========================================================

def validate_entities(entities):
    """
    Remove invalid entities.
    """

    cleaned = []

    for name, entity_type in entities:

        name = clean_text(name)

        if not valid_entity(name):
            continue

        cleaned.append(

            (
                name,
                entity_type
            )

        )

    return cleaned


# ==========================================================
# Remove Duplicates
# ==========================================================

def remove_duplicates(entities):
    """
    Remove duplicate entities while
    preserving insertion order.
    """

    unique = []

    seen = set()

    for name, entity_type in entities:

        key = (
            normalize(name),
            entity_type
        )

        if key in seen:

            continue

        seen.add(key)

        unique.append((name, entity_type))

    return unique


# ==========================================================
# Sort Entities
# ==========================================================

ENTITY_PRIORITY = {

    "MISSION": 1,

    "ORGANIZATION": 2,

    "CENTRE": 3,

    "SPACEPORT": 4,

    "FACILITY": 5,

    "LABORATORY": 6,

    "LAUNCH_VEHICLE": 7,

    "ROCKET_VARIANT": 8,

    "SATELLITE": 9,

    "SPACECRAFT": 10,

    "PAYLOAD": 11,

    "INSTRUMENT": 12,

    "ASTRONAUT": 13,

    "SCIENTIST": 14,

    "COUNTRY": 15,

    "STATE": 16,

    "CITY": 17,

    "PROGRAM": 18,

    "TECHNOLOGY": 19,

    "CELESTIAL_BODY": 20,

    "PERSON": 21,

    "LOCATION": 22

}


def sort_entities(entities):
    """
    Sort entities according to KG priority.
    """

    return sorted(

        entities,

        key=lambda x: (

            ENTITY_PRIORITY.get(

                x[1],
                999

            ),

            x[0]

        )

    )

# ==========================================================
# Main Extraction Pipeline
# ==========================================================

def extract_custom_entities(text):
    """
    Extract all entities from text.

    Pipeline
    --------
    1. Dictionary Lookup
    2. Regex Lookup
    3. spaCy Lookup
    4. Validation
    5. Remove Duplicates
    6. Sort

    NOTE:
    Alias resolution is performed separately in
    entity_resolver.py.
    """

    if not text:
        return []

    text = clean_text(text)

    entities = []

    # Dictionary extraction
    entities.extend(
        dictionary_lookup(text)
    )

    # Regex extraction
    entities.extend(
        regex_lookup(text)
    )

    # spaCy extraction
    entities.extend(
        spacy_lookup(text)
    )

    # Remove invalid entities
    entities = validate_entities(
        entities
    )

    # Remove duplicates
    entities = remove_duplicates(
        entities
    )

    # Sort entities
    entities = sort_entities(
        entities
    )

    return entities


# ==========================================================
# Generic Entity Extraction
# ==========================================================

def extract_entities_by_type(text, entity_type):
    """
    Extract entities of a specific type.
    """

    return [

        entity

        for entity, label

        in extract_custom_entities(text)

        if label == entity_type

    ]


# ==========================================================
# Mission Extraction
# ==========================================================

def extract_missions(text):

    return extract_entities_by_type(

        text,

        "MISSION"

    )


# ==========================================================
# Organization Extraction
# ==========================================================

def extract_organizations(text):

    return extract_entities_by_type(

        text,

        "ORGANIZATION"

    )


# ==========================================================
# Centre Extraction
# ==========================================================

def extract_centres(text):

    return extract_entities_by_type(

        text,

        "CENTRE"

    )


# ==========================================================
# Launch Vehicle Extraction
# ==========================================================

def extract_launch_vehicle(text):

    vehicles = []

    vehicles.extend(

        extract_entities_by_type(

            text,

            "LAUNCH_VEHICLE"

        )

    )

    vehicles.extend(

        extract_entities_by_type(

            text,

            "ROCKET_VARIANT"

        )

    )

    return sorted(

        set(vehicles)

    )


# ==========================================================
# Satellite Extraction
# ==========================================================

def extract_satellites(text):

    return extract_entities_by_type(

        text,

        "SATELLITE"

    )


# ==========================================================
# Spacecraft Extraction
# ==========================================================

def extract_spacecraft(text):

    return extract_entities_by_type(

        text,

        "SPACECRAFT"

    )


# ==========================================================
# Payload Extraction
# ==========================================================

def extract_payloads(text):

    payloads = []

    payloads.extend(

        extract_entities_by_type(

            text,

            "PAYLOAD"

        )

    )

    payloads.extend(

        extract_entities_by_type(

            text,

            "INSTRUMENT"

        )

    )

    return sorted(

        set(payloads)

    )


# ==========================================================
# Scientist Extraction
# ==========================================================

def extract_scientists(text):

    return extract_entities_by_type(

        text,

        "SCIENTIST"

    )


# ==========================================================
# Astronaut Extraction
# ==========================================================

def extract_astronauts(text):

    return extract_entities_by_type(

        text,

        "ASTRONAUT"

    )


# ==========================================================
# Technology Extraction
# ==========================================================

def extract_technologies(text):

    return extract_entities_by_type(

        text,

        "TECHNOLOGY"

    )


# ==========================================================
# Celestial Body Extraction
# ==========================================================

def extract_celestial_bodies(text):

    return extract_entities_by_type(

        text,

        "CELESTIAL_BODY"

    )


# ==========================================================
# Country Extraction
# ==========================================================

def extract_countries(text):

    return extract_entities_by_type(

        text,

        "COUNTRY"

    )


# ==========================================================
# City Extraction
# ==========================================================

def extract_cities(text):

    return extract_entities_by_type(

        text,

        "CITY"

    )


# ==========================================================
# State Extraction
# ==========================================================

def extract_states(text):

    return extract_entities_by_type(

        text,

        "STATE"

    )


# ==========================================================
# Spaceport Extraction
# ==========================================================

def extract_spaceports(text):

    return extract_entities_by_type(

        text,

        "SPACEPORT"

    )


# ==========================================================
# Facility Extraction
# ==========================================================

def extract_facilities(text):

    return extract_entities_by_type(

        text,

        "FACILITY"

    )


# ==========================================================
# Laboratory Extraction
# ==========================================================

def extract_laboratories(text):

    return extract_entities_by_type(

        text,

        "LABORATORY"

    )


# ==========================================================
# Program Extraction
# ==========================================================

def extract_programs(text):

    return extract_entities_by_type(

        text,

        "PROGRAM"

    )


# ==========================================================
# Entity Summary
# ==========================================================

def summarize_entities(text):
    """
    Group extracted entities by type.
    """

    summary = {}

    for entity, entity_type in extract_custom_entities(text):

        summary.setdefault(

            entity_type,

            []

        ).append(entity)

    return summary


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    sample = """
    ISRO launched Chandrayaan-3 using LVM3-M4
    from Satish Dhawan Space Centre.

    Vikram deployed Pragyan.

    The rover carried ChaSTE, ILSA,
    SHAPE and RAMBHA-LP.

    NASA and ISRO are collaborating
    on the NISAR mission.

    Aditya-L1 carries VELC,
    SUIT and HEL1OS.
    """

    print("=" * 70)
    print("Extracted Entities")
    print("=" * 70)

    for entity in extract_custom_entities(sample):
        print(entity)

    print("=" * 70)

    print("\nGrouped Summary\n")

    from pprint import pprint

    pprint(summarize_entities(sample))