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

from dataclasses import dataclass, field
from collections import defaultdict
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
# Entity Extractor Configuration
# ==========================================================

ENABLE_DICTIONARY = True

ENABLE_REGEX = True

ENABLE_SPACY = True

ENABLE_CONTEXT_VALIDATION = True

ENABLE_CONFIDENCE = True

ENABLE_DUPLICATE_FUSION = True

ENABLE_ENTITY_NORMALIZATION = True

PRINT_EXTRACTION_STATISTICS = True

MIN_ENTITY_CONFIDENCE = 0.70

# ==========================================================
# Confidence Scores
# ==========================================================

CONFIDENCE = {

    "DICTIONARY": 0.99,

    "REGEX": 0.95,

    "SPACY": 0.75,

    "CONTEXT_MATCH": 0.90,

    "ALIAS_MATCH": 0.92

}

# ==========================================================
# Entity Object
# ==========================================================

@dataclass
class ExtractedEntity:

    name: str

    entity_type: str

    confidence: float

    source: str

    method: str

    sentence: str = ""

    canonical_name: str = ""

    sources: list = field(default_factory=list)

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
# Extraction Statistics
# ==========================================================

class ExtractionStatistics:

    def __init__(self):

        self.dictionary_entities = 0
        self.regex_entities = 0
        self.spacy_entities = 0

        self.filtered_entities = 0
        self.low_confidence = 0
        self.alias_merged = 0
        self.duplicates_removed = 0

        self.final_entities = 0

    def print_summary(self):

        if not PRINT_EXTRACTION_STATISTICS:
            return

        print()

        print("=" * 70)
        print("ENTITY EXTRACTION REPORT")
        print("=" * 70)

        print(f"Dictionary Matches : {self.dictionary_entities}")
        print(f"Regex Matches      : {self.regex_entities}")
        print(f"spaCy Matches      : {self.spacy_entities}")

        print("-" * 70)

        print(f"Filtered           : {self.filtered_entities}")
        print(f"Low Confidence     : {self.low_confidence}")
        print(f"Alias Merged       : {self.alias_merged}")
        print(f"Duplicates Removed : {self.duplicates_removed}")

        print("-" * 70)

        print(f"Final Entities     : {self.final_entities}")

        print("=" * 70)


extractor_stats = ExtractionStatistics()

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

MISSION_PATTERNS = [

    r"\bChandrayaan[- ]?\d+\b",

    r"\bMangalyaan\b",

    r"\bAditya[- ]?L1\b",

    r"\bSpaDeX\b",

    r"\bNISAR\b",

    r"\bGaganyaan\b",

    r"\bAstroSat\b"

]


SPACECRAFT_PATTERNS = [

    r"\bVikram\b",

    r"\bPragyan\b",

    r"\bOrbiter\b",

    r"\bLander\b",

    r"\bRover\b"

]


LAUNCH_VEHICLE_PATTERNS = [

    r"\bPSLV\b",

    r"\bGSLV\b",

    r"\bSSLV\b",

    r"\bLVM3\b"

]


PROGRAM_PATTERNS = [

    r"\bIndian Human Spaceflight Programme\b",

    r"\bGaganyaan Programme\b",

    r"\bLunar Exploration Programme\b"

]

# ==========================================================
# Confidence Helper
# ==========================================================

def get_confidence(method):

    return CONFIDENCE.get(
        method,
        0.50
    )

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

# ==========================================================
# Canonical Name
# ==========================================================

def canonicalize(name):

    name = clean_text(name)

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    name = re.sub(
        r"\s*-\s*",
        "-",
        name
    )

    return name.strip()


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
    
    if name.endswith((".", ":", ";", ",")):
        return False
    
    if (
        name.isupper()
        and len(name) <= 2
        and name not in {"ISRO", "NASA", "ESA", "DRDO"}
    ):
        return False

    return True

# ==========================================================
# Context Validation
# ==========================================================

INVALID_ORGANIZATIONS = {

    "lox",
    "hydrogen",
    "oxygen",
    "cryogenic",
    "microgravity",
    "animation",
    "halo",
    "velocity",
    "temperature",
    "pressure",
    "rocket",
    "mission",
    "spacecraft",
    "satellite",
    "payload",
    "instrument",
    "science",
    "orbit",
    "launch",
    "launches",
    "space",
    "vehicle"

}

INVALID_LOCATIONS = {

    "orbit",

    "moon",

    "mars",

    "sun",

    "earth",

    "l1",

    "l2"

}

INVALID_PERSONS = {

    "mission",

    "satellite",

    "payload",

    "instrument"

}


VALID_ORG_KEYWORDS = {

    "agency",
    "organisation",
    "organization",
    "centre",
    "center",
    "laboratory",
    "lab",
    "corporation",
    "company",
    "institute",
    "department"

}

INVALID_SPACECRAFT = {

    "rover",

    "lander",

    "orbiter",

    "spacecraft"

}


def validate_context(entity, sentence):

    name = entity.name.lower()

    if entity.entity_type == "PERSON":

        if name in INVALID_PERSONS:
            return False

    elif entity.entity_type == "LOCATION":

        if name in INVALID_LOCATIONS:
            return False

    elif entity.entity_type == "SPACECRAFT":

        if name in INVALID_SPACECRAFT:
            return False

    elif entity.entity_type == "ORGANIZATION":

        if name in INVALID_ORGANIZATIONS:
            return False

    if len(entity.name.split()) >= 3:
        entity.confidence = min(entity.confidence + 0.05, 1.0)

    if entity.name.isupper():
        entity.confidence = min(entity.confidence + 0.03, 1.0)

    return True

# ==========================================================
# Entity Aliases
# ==========================================================

ENTITY_ALIASES = {

    # ---------------- Missions ----------------

    "Aditya L1": "Aditya-L1",
    "ADITYA L1": "Aditya-L1",
    "AdityaL1": "Aditya-L1",

    "Chandrayaan 1": "Chandrayaan-1",
    "Chandrayaan 2": "Chandrayaan-2",
    "Chandrayaan 3": "Chandrayaan-3",

    "MOM": "Mars Orbiter Mission",

    "Mars Orbiter": "Mars Orbiter Mission",

    "SpaDex": "SpaDeX",

    # ---------------- Rockets ----------------

    "LVM-3": "LVM3",

    "GSLV Mk III": "LVM3",

    "GSLV Mark III": "LVM3",

    "PSLV XL": "PSLV-XL",

    # ---------------- Organizations ----------------

    "Indian Space Research Organisation": "ISRO",

    "Indian Space Research Organization": "ISRO",

    "National Aeronautics and Space Administration": "NASA",

    "European Space Agency": "ESA",

}

# ==========================================================
# Alias Resolver
# ==========================================================

def resolve_alias(name):

    canonical = ENTITY_ALIASES.get(
        name,

        name
    )

    return canonical

# ==========================================================
# Entity Normalization
# ==========================================================

def normalize_entity_name(name):

    name = canonicalize(name)

    name = resolve_alias(name)

    return name

# ==========================================================
# Entity Similarity
# ==========================================================

def are_same_entity(

    entity1,

    entity2

):

    if entity1.entity_type != entity2.entity_type:

        return False

    return (

        normalize_entity_name(

            entity1.name

        )

        ==

        normalize_entity_name(

            entity2.name

        )

    )

# ==========================================================
# Entity Fusion
# ==========================================================

def fuse_entities(

    entities

):

    fused = []

    for entity in entities:

        found = False

        for existing in fused:

            if are_same_entity(

                entity,

                existing

            ):

                existing.confidence = max(

                    existing.confidence,

                    entity.confidence

                )

                if entity.source not in existing.sources:
                    existing.sources.append(entity.source)

                extractor_stats.alias_merged += 1

                found = True

                break

        if not found:

            entity.name = normalize_entity_name(

                entity.name

            )

            entity.canonical_name = entity.name

            fused.append(

                entity

            )
        
        for entity in fused:

            if len(entity.sources) >= 2:

                entity.confidence = min(

                    entity.confidence + 0.05,

                    1.0

                )

    return fused

# ==========================================================
# Longest Match Sorting
# ==========================================================

def sort_dictionary_values(values):

    return sorted(

        values,

        key=len,

        reverse=True

    )

# ==========================================================
# Dictionary Lookup
# ==========================================================

def dictionary_lookup(text):
    """
    Dictionary Engine V2

    Features
    --------
    ✓ Longest match first
    ✓ Alias resolution
    ✓ Canonical names
    ✓ Confidence support
    ✓ Duplicate prevention
    """

    entities = []

    matched = set()

    lower_text = normalize(text)

    for entity_type, values in ENTITY_LOOKUP.items():

        values = sort_dictionary_values(values)

        for value in values:

            pattern = r"\b" + re.escape(value.lower()) + r"\b"

            alias = normalize_entity_name(value)

            if not re.search(pattern, lower_text):
                continue

            key = (

                normalize(alias),

                entity_type

            )

            if key in matched:
                continue

            matched.add(key)

            extractor_stats.dictionary_entities += 1

            entities.append(

                ExtractedEntity(

                    name=alias,

                    entity_type=entity_type,

                    confidence=get_confidence("DICTIONARY"),

                    source="Dictionary",

                    method="DICTIONARY",

                    sentence="",

                    canonical_name=alias,

                    sources=["Dictionary"]

                )

            )

    return entities

# ==========================================================
# Regex Extraction Helper V2
# ==========================================================

def extract_by_patterns(text, patterns, entity_type):

    entities = []

    matched = set()

    for pattern in patterns:

        matches = re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            value = normalize_entity_name(match.group())

            key = (
                normalize(value),
                entity_type
            )

            if key in matched:
                continue

            matched.add(key)

            extractor_stats.regex_entities += 1

            entities.append(

                ExtractedEntity(

                    name=value,

                    entity_type=entity_type,

                    confidence=get_confidence("REGEX"),

                    source="Regex",

                    method="REGEX",

                    sentence="",

                    canonical_name=value,

                    sources=["Regex"]

                )

            )

    return entities

# ==========================================================
# Regex Extraction
# ==========================================================

def regex_lookup(text):

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
            LAUNCH_VEHICLE_PATTERNS,
            "LAUNCH_VEHICLE"
        )

    )

    entities.extend(

        extract_by_patterns(
            text,
            SATELLITE_PATTERNS,
            "SATELLITE"
        )

    )

    entities.extend(

        extract_by_patterns(
            text,
            MISSION_PATTERNS,
            "MISSION"
        )

    )

    entities.extend(

        extract_by_patterns(
            text,
            SPACECRAFT_PATTERNS,
            "SPACECRAFT"
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
            PROGRAM_PATTERNS,
            "PROGRAM"
        )

    )

    return entities

# ==========================================================
# Sentence Splitter
# ==========================================================

def split_sentences(text):

    doc = nlp(text)

    return [

        sent.text.strip()

        for sent

        in doc.sents

    ]

# ==========================================================
# spaCy Label Mapping
# ==========================================================

SPACY_LABEL_MAP = {

    "ORG": "ORGANIZATION",

    "PERSON": "PERSON",

    "GPE": "LOCATION",

    "LOC": "LOCATION",

    "FAC": "FACILITY"

}

# ==========================================================
# Domain Entity Types
# ==========================================================

DOMAIN_ENTITY_TYPES = {

    "MISSION",

    "PAYLOAD",

    "SPACECRAFT",

    "SATELLITE",

    "LAUNCH_VEHICLE",

    "ROCKET_VARIANT",

    "PROGRAM"

}

# ==========================================================
# spaCy Extraction V2
# ==========================================================

def spacy_lookup(text):

    entities = []

    matched = set()

    sentences = split_sentences(text)

    ORG_BLACKLIST = {

        "announcement",
        "mission",
        "missions",
        "press",
        "release",
        "news",
        "home",
        "paper",
        "journal",
        "study",
        "conference",
        "event",
        "document",
        "figure",
        "results",
        "rover",
        "lander",
        "orbiter",
        "spacecraft"

    }

    for sentence in sentences:

        doc = nlp(sentence)

        for ent in doc.ents:

            value = normalize_entity_name(ent.text)

            if not valid_entity(value):
                continue

            # ----------------------------------------
            # Give Dictionary/Regex priority
            # ----------------------------------------

            domain_type = None

            for dtype in DOMAIN_ENTITY_TYPES:

                if value in ENTITY_LOOKUP.get(dtype, set()):

                    domain_type = dtype
                    break

            if domain_type is not None:

                entity_type = domain_type

            else:

                entity_type = SPACY_LABEL_MAP.get(ent.label_)

                if entity_type is None:
                    continue

            # ----------------------------------------
            # Additional organization validation
            # ----------------------------------------

            if entity_type == "ORGANIZATION":

                lower = value.lower()

                if (
                    lower in ORG_BLACKLIST
                    or len(value.split()) > 4
                ):
                    continue

            # ----------------------------------------
            # Duplicate detection
            # ----------------------------------------

            key = (

                normalize_entity_name(value),

                entity_type

            )

            if key in matched:
                continue

            matched.add(key)

            extractor_stats.spacy_entities += 1

            candidate = ExtractedEntity(

                name=value,

                entity_type=entity_type,

                confidence=get_confidence("SPACY"),

                source="spaCy",

                method="SPACY",

                sentence=sentence,

                canonical_name=value,

                sources=["spaCy"]

            )

            # ----------------------------------------
            # Context validation
            # ----------------------------------------

            if ENABLE_CONTEXT_VALIDATION:

                if not validate_context(candidate, sentence):

                    extractor_stats.filtered_entities += 1

                    continue

            entities.append(candidate)

    return entities

# ==========================================================
# Entity Validation V2
# ==========================================================

def validate_entities(entities):

    cleaned = []

    for entity in entities:

        if not valid_entity(

            entity.name

        ):

            extractor_stats.filtered_entities += 1

            continue

        cleaned.append(

            entity

        )

    return cleaned

# ==========================================================
# Confidence Filtering
# ==========================================================

def filter_low_confidence_entities(entities):

    accepted = []

    for entity in entities:

        if entity.confidence < MIN_ENTITY_CONFIDENCE:

            extractor_stats.low_confidence += 1

            continue

        accepted.append(entity)

    return accepted

# ==========================================================
# Remove Duplicate Entities V2
# ==========================================================

def remove_duplicates(

    entities

):

    unique = []

    seen = set()

    for entity in entities:

        key = (

            normalize_entity_name(

                entity.name

            ),

            entity.entity_type

        )

        if key in seen:

            extractor_stats.duplicates_removed += 1

            continue

        seen.add(key)

        unique.append(entity)

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


def sort_entities(

    entities

):

    return sorted(

        entities,

        key=lambda entity: (

            ENTITY_PRIORITY.get(

                entity.entity_type,

                999

            ),

            -entity.confidence,

            normalize_entity_name(
                entity.name
            )

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

    # Dictionary

    if ENABLE_DICTIONARY:

        entities.extend(

            dictionary_lookup(text)

        )

    # Regex

    if ENABLE_REGEX:

        entities.extend(

            regex_lookup(text)

        )

    # spaCy

    if ENABLE_SPACY:

        entities.extend(

            spacy_lookup(text)

        )

    # Validation

    entities = validate_entities(

        entities

    )

    entities = filter_low_confidence_entities(

        entities

    )

    entities = fuse_entities(

        entities

    )

    # Duplicate Removal

    entities = remove_duplicates(

        entities

    )

    # Sorting

    entities = sort_entities(

        entities

    )

    extractor_stats.final_entities = len(

        entities

    )

    extractor_stats.print_summary()

    # Convert back to tuples

    return [

        (

            entity.name,

            entity.entity_type

        )

        for entity

        in entities

    ]

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