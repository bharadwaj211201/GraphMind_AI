"""
==========================================================
Entity Resolver V2
==========================================================

Purpose
-------
Convert extracted entities into their canonical forms before
building the Knowledge Graph.

Responsibilities
----------------
1. Normalize text
2. Resolve aliases
3. Standardize ontology names
4. Preserve rocket variants
5. Optional fuzzy matching
6. Cross-type validation
7. Confidence scoring
8. Remove duplicate entities
9. Generate resolver statistics

Author
------
ISRO Knowledge Graph Project
"""

import re
from difflib import get_close_matches
from collections import defaultdict

from scrapers.domain_entities import (

    # Alias Dictionaries
    MISSION_ALIASES,
    ORGANIZATION_ALIASES,
    CENTRE_ALIASES,

    # Ontologies
    MISSIONS,
    ORGANIZATIONS,
    CENTRES,

    LAUNCH_VEHICLES,
    ROCKET_VARIANTS,

    SATELLITES,
    SPACECRAFT,

    PAYLOADS,
    INSTRUMENTS,

    SCIENTISTS,
    ASTRONAUTS,

    COUNTRIES,
    STATES,
    CITIES,

    SPACEPORTS,
    FACILITIES,
    LABORATORIES,

    PROGRAMS,
    TECHNOLOGIES,
    CELESTIAL_BODIES
)

# ==========================================================
# Configuration
# ==========================================================

ENABLE_FUZZY_MATCHING = True

FUZZY_THRESHOLD = 0.92

ENABLE_CROSS_TYPE_VALIDATION = True

PRINT_STATISTICS = True

# ==========================================================
# Normalization
# ==========================================================

def normalize(text):
    """
    Normalize entity names for comparison.

    Examples
    --------
    Chandrayaan-3
    Chandrayaan 3
    CHANDRAYAAN_3

    →

    chandrayaan 3
    """

    if not text:
        return ""

    text = str(text)

    text = text.lower()

    text = text.strip()

    text = text.replace("-", " ")

    text = text.replace("_", " ")

    text = text.replace("/", " ")

    text = text.replace(".", "")

    text = text.replace(",", "")

    text = text.replace("(", "")

    text = text.replace(")", "")

    text = text.replace("’", "'")

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"^the\s+", "", text)

    text = re.sub(r"'s$", "", text)

    return text

# ==========================================================
# Rocket Variant Detection
# ==========================================================

ROCKET_PATTERNS = [

    r"PSLV-[A-Z0-9]+",

    r"GSLV-[A-Z0-9]+",

    r"LVM3-[A-Z0-9]+",

    r"SSLV-[A-Z0-9]+",

    r"PSLV\s+[A-Z0-9]+",

    r"GSLV\s+[A-Z0-9]+",

    r"LVM3\s+[A-Z0-9]+",

    r"SSLV\s+[A-Z0-9]+"
]


def is_rocket_variant(name):
    """
    Detect rocket variants such as

    PSLV-C62
    GSLV-F15
    LVM3-M5
    SSLV-D3
    """

    text = name.upper().strip()

    for pattern in ROCKET_PATTERNS:

        if re.fullmatch(pattern, text):

            return True

    return False


# ==========================================================
# Build Lookup Dictionaries
# ==========================================================

def build_lookup(ontology):
    """
    Build

    normalized name

        →

    canonical ontology name

    for O(1) lookup.
    """

    lookup = {}

    for item in ontology:

        lookup[normalize(item)] = item

    return lookup


MISSION_LOOKUP = build_lookup(MISSIONS)

ORGANIZATION_LOOKUP = build_lookup(ORGANIZATIONS)

CENTRE_LOOKUP = build_lookup(CENTRES)

LAUNCH_VEHICLE_LOOKUP = build_lookup(LAUNCH_VEHICLES)

SATELLITE_LOOKUP = build_lookup(SATELLITES)

SPACECRAFT_LOOKUP = build_lookup(SPACECRAFT)

PAYLOAD_LOOKUP = build_lookup(PAYLOADS)

INSTRUMENT_LOOKUP = build_lookup(INSTRUMENTS)

SCIENTIST_LOOKUP = build_lookup(SCIENTISTS)

ASTRONAUT_LOOKUP = build_lookup(ASTRONAUTS)

COUNTRY_LOOKUP = build_lookup(COUNTRIES)

STATE_LOOKUP = build_lookup(STATES)

CITY_LOOKUP = build_lookup(CITIES)

SPACEPORT_LOOKUP = build_lookup(SPACEPORTS)

FACILITY_LOOKUP = build_lookup(FACILITIES)

LABORATORY_LOOKUP = build_lookup(LABORATORIES)

PROGRAM_LOOKUP = build_lookup(PROGRAMS)

TECHNOLOGY_LOOKUP = build_lookup(TECHNOLOGIES)

CELESTIAL_BODY_LOOKUP = build_lookup(CELESTIAL_BODIES)

# ==========================================================
# Alias Lookup
# ==========================================================

ALIAS_TABLE = {

    "MISSION": MISSION_ALIASES,

    "ORGANIZATION": ORGANIZATION_ALIASES,

    "CENTRE": CENTRE_ALIASES
}

# ==========================================================
# Ontology Lookup Table
# ==========================================================

LOOKUP_TABLE = {

    "MISSION": MISSION_LOOKUP,

    "ORGANIZATION": ORGANIZATION_LOOKUP,

    "CENTRE": CENTRE_LOOKUP,

    "LAUNCH_VEHICLE": LAUNCH_VEHICLE_LOOKUP,

    "ROCKET_VARIANT": LAUNCH_VEHICLE_LOOKUP,

    "SATELLITE": SATELLITE_LOOKUP,

    "SPACECRAFT": SPACECRAFT_LOOKUP,

    "PAYLOAD": PAYLOAD_LOOKUP,

    "INSTRUMENT": INSTRUMENT_LOOKUP,

    "SCIENTIST": SCIENTIST_LOOKUP,

    "ASTRONAUT": ASTRONAUT_LOOKUP,

    "COUNTRY": COUNTRY_LOOKUP,

    "STATE": STATE_LOOKUP,

    "CITY": CITY_LOOKUP,

    "SPACEPORT": SPACEPORT_LOOKUP,

    "FACILITY": FACILITY_LOOKUP,

    "LABORATORY": LABORATORY_LOOKUP,

    "PROGRAM": PROGRAM_LOOKUP,

    "TECHNOLOGY": TECHNOLOGY_LOOKUP,

    "CELESTIAL_BODY": CELESTIAL_BODY_LOOKUP
}

# ==========================================================
# Resolver Statistics
# ==========================================================

class ResolverStatistics:

    def __init__(self):

        self.total_entities = 0

        self.alias_matches = 0

        self.ontology_matches = 0

        self.fuzzy_matches = 0

        self.rocket_variants = 0

        self.cross_type_corrections = 0

        self.duplicates_removed = 0

        self.unknown_entities = 0

    def print_summary(self):

        if not PRINT_STATISTICS:
            return

        print("\n" + "=" * 70)
        print("ENTITY RESOLVER STATISTICS")
        print("=" * 70)

        print(f"Entities Processed      : {self.total_entities}")
        print(f"Alias Matches           : {self.alias_matches}")
        print(f"Ontology Matches        : {self.ontology_matches}")
        print(f"Fuzzy Matches           : {self.fuzzy_matches}")
        print(f"Rocket Variants         : {self.rocket_variants}")
        print(f"Cross-Type Corrections  : {self.cross_type_corrections}")
        print(f"Duplicates Removed      : {self.duplicates_removed}")
        print(f"Unknown Entities        : {self.unknown_entities}")

        print("=" * 70)


resolver_stats = ResolverStatistics()

# ==========================================================
# Generic Lookup
# ==========================================================

def lookup_entity(name, entity_type):
    """
    Resolve an entity using the following order:

    1. Rocket Variant
    2. Alias Dictionary
    3. Ontology Lookup
    4. Fuzzy Matching
    """

    normalized = normalize(name)

    # ------------------------------------------------------
    # Rocket Variant
    # ------------------------------------------------------

    if entity_type in ("LAUNCH_VEHICLE", "ROCKET_VARIANT"):

        if is_rocket_variant(name):

            resolver_stats.rocket_variants += 1

            return {
                "name": name.upper(),
                "confidence": 1.0,
                "matched_by": "rocket_variant"
            }

    # ------------------------------------------------------
    # Alias Lookup
    # ------------------------------------------------------

    alias_dict = ALIAS_TABLE.get(entity_type)

    if alias_dict:

        if normalized in alias_dict:

            resolver_stats.alias_matches += 1

            return {
                "name": alias_dict[normalized],
                "confidence": 1.0,
                "matched_by": "alias"
            }

    # ------------------------------------------------------
    # Ontology Lookup
    # ------------------------------------------------------

    ontology = LOOKUP_TABLE.get(entity_type)

    if ontology:

        if normalized in ontology:

            resolver_stats.ontology_matches += 1

            return {
                "name": ontology[normalized],
                "confidence": 1.0,
                "matched_by": "ontology"
            }

    # ------------------------------------------------------
    # Fuzzy Matching
    # ------------------------------------------------------

    if ENABLE_FUZZY_MATCHING and ontology:

        matches = get_close_matches(

            normalized,

            ontology.keys(),

            n=1,

            cutoff=FUZZY_THRESHOLD

        )

        if matches:

            resolver_stats.fuzzy_matches += 1

            return {

                "name": ontology[matches[0]],

                "confidence": 0.90,

                "matched_by": "fuzzy"

            }

    resolver_stats.unknown_entities += 1

    return {

        "name": name,

        "confidence": 0.50,

        "matched_by": "unknown"

    }


# ==========================================================
# Cross-Type Validation
# ==========================================================

def detect_entity_type(name):
    """
    Detect if an entity actually belongs to
    another ontology.

    Example

    PSLV

    extracted as

    MISSION

    →

    corrected to

    LAUNCH_VEHICLE
    """

    normalized = normalize(name)

    for entity_type, lookup in LOOKUP_TABLE.items():

        if normalized in lookup:

            return entity_type

    return None


def validate_entity_type(name, current_type):
    """
    Correct entity type if necessary.
    """

    if not ENABLE_CROSS_TYPE_VALIDATION:

        return current_type

    detected = detect_entity_type(name)

    if detected and detected != current_type:

        resolver_stats.cross_type_corrections += 1

        return detected

    return current_type


# ==========================================================
# Resolve One Entity
# ==========================================================

def resolve_entity(entity_name, entity_type):
    """
    Resolve one entity.

    Returns

    {
        name
        type
        original_name
        confidence
        matched_by
        resolved
    }
    """

    resolver_stats.total_entities += 1

    # --------------------------------------------
    # Validate Type
    # --------------------------------------------

    entity_type = validate_entity_type(

        entity_name,

        entity_type

    )

    # --------------------------------------------
    # Lookup
    # --------------------------------------------

    result = lookup_entity(

        entity_name,

        entity_type

    )

    canonical = result["name"]

    return {

        "name": canonical,

        "type": entity_type,

        "original_name": entity_name,

        "confidence": result["confidence"],

        "matched_by": result["matched_by"],

        "resolved": normalize(canonical) != normalize(entity_name)

    }


# ==========================================================
# Resolve Entity List
# ==========================================================

def resolve_entities(entity_list):
    """
    Resolve all extracted entities.

    Input

    [
        ("ISRO","ORGANIZATION"),
        ("PSLV","MISSION")
    ]

    Output

    [
        {...},
        {...}
    ]
    """

    resolved_entities = []

    seen = set()

    for entity_name, entity_type in entity_list:

        entity = resolve_entity(

            entity_name,

            entity_type

        )

        key = (

            normalize(entity["name"]),

            entity["type"]

        )

        if key in seen:

            resolver_stats.duplicates_removed += 1

            continue

        seen.add(key)

        resolved_entities.append(entity)

    return resolved_entities

# ==========================================================
# Group Entities
# ==========================================================

def group_entities(entity_list):
    """
    Group resolved entities by entity type.

    Returns
    -------
    {
        "MISSION": [...],
        "ORGANIZATION": [...]
    }
    """

    grouped = defaultdict(list)

    for entity in entity_list:

        grouped[entity["type"]].append(entity)

    return dict(grouped)


# ==========================================================
# Pretty Printer
# ==========================================================

def print_entities(entity_list):
    """
    Pretty-print resolved entities.
    """

    grouped = group_entities(entity_list)

    print("\n" + "=" * 80)
    print("RESOLVED ENTITIES")
    print("=" * 80)

    for entity_type in sorted(grouped):

        print("\n" + "-" * 80)
        print(entity_type)
        print("-" * 80)

        for entity in grouped[entity_type]:

            if entity["resolved"]:

                print(
                    f"{entity['original_name']}"
                    f"  -->  "
                    f"{entity['name']}"
                    f"  [{entity['matched_by']}]"
                    f"  Confidence={entity['confidence']:.2f}"
                )

            else:

                print(
                    f"{entity['name']}"
                    f"  [{entity['matched_by']}]"
                    f"  Confidence={entity['confidence']:.2f}"
                )


# ==========================================================
# Export Statistics
# ==========================================================

def get_statistics():
    """
    Return resolver statistics as a dictionary.
    """

    return {

        "entities_processed":
            resolver_stats.total_entities,

        "alias_matches":
            resolver_stats.alias_matches,

        "ontology_matches":
            resolver_stats.ontology_matches,

        "fuzzy_matches":
            resolver_stats.fuzzy_matches,

        "rocket_variants":
            resolver_stats.rocket_variants,

        "cross_type_corrections":
            resolver_stats.cross_type_corrections,

        "duplicates_removed":
            resolver_stats.duplicates_removed,

        "unknown_entities":
            resolver_stats.unknown_entities
    }


# ==========================================================
# Print Statistics
# ==========================================================

def print_statistics():

    resolver_stats.print_summary()


# ==========================================================
# Reset Statistics
# ==========================================================

def reset_statistics():
    """
    Reset counters before processing a new batch.
    """

    global resolver_stats

    resolver_stats = ResolverStatistics()


# ==========================================================
# Test Block
# ==========================================================

if __name__ == "__main__":

    sample_entities = [

        ("Indian Space Research Organisation",
         "ORGANIZATION"),

        ("ISRO",
         "ORGANIZATION"),

        ("Chandrayaan 3",
         "MISSION"),

        ("Chandrayan-3",
         "MISSION"),

        ("PSLV-C62",
         "ROCKET_VARIANT"),

        ("LVM3",
         "LAUNCH_VEHICLE"),

        ("NASA",
         "ORGANIZATION"),

        ("National Aeronautics and Space Administration",
         "ORGANIZATION"),

        ("Vikram",
         "SPACECRAFT"),

        ("Pragyan",
         "SPACECRAFT"),

        ("Aditya L1",
         "MISSION"),

        ("Aditya-L1",
         "SATELLITE"),

        ("Mars Orbiter Mission",
         "MISSION"),

        ("Mangalyaan",
         "SATELLITE"),

        ("Satish Dhawan Space Centre",
         "SPACEPORT"),

        ("SDSC",
         "SPACEPORT"),

        ("Moon",
         "CELESTIAL_BODY"),

        ("Mars",
         "CELESTIAL_BODY"),

        ("PSLV",
         "MISSION"),

        ("SSLV-D3",
         "ROCKET_VARIANT")

    ]

    print("\n")
    print("=" * 80)
    print("ENTITY RESOLVER V2")
    print("=" * 80)

    resolved = resolve_entities(sample_entities)

    print_entities(resolved)

    print_statistics()

    print("\nStatistics Dictionary\n")

    print(get_statistics())

    print("\nFinished.\n")