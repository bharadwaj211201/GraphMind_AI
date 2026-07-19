"""
==========================================================
Entity Resolver
==========================================================

This module converts extracted entities into their
canonical forms before storing them in MongoDB or Neo4j.

Responsibilities
----------------
1. Normalize text
2. Resolve aliases
3. Standardize entity names
4. Preserve rocket variants
5. Remove duplicate entities

NOTE
----
This module DOES NOT classify entities.

Classification is handled by
entity_classifier.py.
"""

import re

from scrapers.domain_entities import (

    MISSION_ALIASES,
    ORGANIZATION_ALIASES,
    CENTRE_ALIASES,

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
# Normalization
# ==========================================================

def normalize(text):
    """
    Normalize entity text.

    Example

    Chandrayaan-3
    Chandrayaan 3
    CHANDRAYAAN_3

    →

    chandrayaan 3
    """

    text = text.lower()

    text = text.strip()

    text = text.replace("-", " ")

    text = text.replace("_", " ")

    text = text.replace("/", " ")

    text = text.replace(".", "")

    text = text.replace("’", "'")

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"^the\s+", "", text)

    text = re.sub(r"'s$", "", text)

    return text


# ==========================================================
# Rocket Variant Detection
# ==========================================================

ROCKET_REGEX = [

    r"PSLV-[A-Z0-9]+",

    r"GSLV-[A-Z0-9]+",

    r"LVM3-[A-Z0-9]+",

    r"SSLV-[A-Z0-9]+"

]


def is_rocket_variant(text):

    for pattern in ROCKET_REGEX:

        if re.fullmatch(

            pattern,

            text.upper()

        ):

            return True

    return False


# ==========================================================
# Canonical Lookup
# ==========================================================

def canonical_lookup(name, ontology):
    """
    Return ontology spelling if found.
    """

    key = normalize(name)

    for value in ontology:

        if normalize(value) == key:

            return value

    return None

# ==========================================================
# Mission Resolver
# ==========================================================

def resolve_mission(name):
    """
    Resolve mission aliases to canonical mission names.
    """

    key = normalize(name)

    # Alias lookup
    if key in MISSION_ALIASES:
        return MISSION_ALIASES[key]

    # Ontology lookup
    canonical = canonical_lookup(name, MISSIONS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Organization Resolver
# ==========================================================

def resolve_organization(name):
    """
    Resolve organization aliases.
    """

    key = normalize(name)

    if key in ORGANIZATION_ALIASES:
        return ORGANIZATION_ALIASES[key]

    canonical = canonical_lookup(name, ORGANIZATIONS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Centre Resolver
# ==========================================================

def resolve_centre(name):
    """
    Resolve ISRO centre aliases.
    """

    key = normalize(name)

    if key in CENTRE_ALIASES:
        return CENTRE_ALIASES[key]

    canonical = canonical_lookup(name, CENTRES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Launch Vehicle Resolver
# ==========================================================

def resolve_vehicle(name):
    """
    Preserve rocket variants while normalizing
    launch vehicle family names.
    """

    # Preserve variants like PSLV-C62
    if is_rocket_variant(name):
        return name.upper()

    canonical = canonical_lookup(name, LAUNCH_VEHICLES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Satellite Resolver
# ==========================================================

def resolve_satellite(name):

    canonical = canonical_lookup(name, SATELLITES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Spacecraft Resolver
# ==========================================================

def resolve_spacecraft(name):

    canonical = canonical_lookup(name, SPACECRAFT)

    if canonical:
        return canonical

    return name


# ==========================================================
# Payload Resolver
# ==========================================================

def resolve_payload(name):

    canonical = canonical_lookup(name, PAYLOADS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Instrument Resolver
# ==========================================================

def resolve_instrument(name):

    canonical = canonical_lookup(name, INSTRUMENTS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Scientist Resolver
# ==========================================================

def resolve_scientist(name):

    canonical = canonical_lookup(name, SCIENTISTS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Astronaut Resolver
# ==========================================================

def resolve_astronaut(name):

    canonical = canonical_lookup(name, ASTRONAUTS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Country Resolver
# ==========================================================

def resolve_country(name):

    canonical = canonical_lookup(name, COUNTRIES)

    if canonical:
        return canonical

    return name


# ==========================================================
# State Resolver
# ==========================================================

def resolve_state(name):

    canonical = canonical_lookup(name, STATES)

    if canonical:
        return canonical

    return name


# ==========================================================
# City Resolver
# ==========================================================

def resolve_city(name):

    canonical = canonical_lookup(name, CITIES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Spaceport Resolver
# ==========================================================

def resolve_spaceport(name):

    canonical = canonical_lookup(name, SPACEPORTS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Facility Resolver
# ==========================================================

def resolve_facility(name):

    canonical = canonical_lookup(name, FACILITIES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Laboratory Resolver
# ==========================================================

def resolve_laboratory(name):

    canonical = canonical_lookup(name, LABORATORIES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Program Resolver
# ==========================================================

def resolve_program(name):

    canonical = canonical_lookup(name, PROGRAMS)

    if canonical:
        return canonical

    return name


# ==========================================================
# Technology Resolver
# ==========================================================

def resolve_technology(name):

    canonical = canonical_lookup(name, TECHNOLOGIES)

    if canonical:
        return canonical

    return name


# ==========================================================
# Celestial Body Resolver
# ==========================================================

def resolve_celestial_body(name):

    canonical = canonical_lookup(name, CELESTIAL_BODIES)

    if canonical:
        return canonical

    return name

# ==========================================================
# Resolve One Entity
# ==========================================================

def resolve_entity(entity_name, entity_type):
    """
    Resolve a single entity and return a structured object.
    """

    if entity_type == "MISSION":
        canonical = resolve_mission(entity_name)

    elif entity_type == "ORGANIZATION":
        canonical = resolve_organization(entity_name)

    elif entity_type == "CENTRE":
        canonical = resolve_centre(entity_name)

    elif entity_type in ("LAUNCH_VEHICLE", "ROCKET_VARIANT"):
        canonical = resolve_vehicle(entity_name)

    elif entity_type == "SATELLITE":
        canonical = resolve_satellite(entity_name)

    elif entity_type == "SPACECRAFT":
        canonical = resolve_spacecraft(entity_name)

    elif entity_type == "PAYLOAD":
        canonical = resolve_payload(entity_name)

    elif entity_type == "INSTRUMENT":
        canonical = resolve_instrument(entity_name)

    elif entity_type == "SCIENTIST":
        canonical = resolve_scientist(entity_name)

    elif entity_type == "ASTRONAUT":
        canonical = resolve_astronaut(entity_name)

    elif entity_type == "COUNTRY":
        canonical = resolve_country(entity_name)

    elif entity_type == "STATE":
        canonical = resolve_state(entity_name)

    elif entity_type == "CITY":
        canonical = resolve_city(entity_name)

    elif entity_type == "SPACEPORT":
        canonical = resolve_spaceport(entity_name)

    elif entity_type == "FACILITY":
        canonical = resolve_facility(entity_name)

    elif entity_type == "LABORATORY":
        canonical = resolve_laboratory(entity_name)

    elif entity_type == "PROGRAM":
        canonical = resolve_program(entity_name)

    elif entity_type == "TECHNOLOGY":
        canonical = resolve_technology(entity_name)

    elif entity_type == "CELESTIAL_BODY":
        canonical = resolve_celestial_body(entity_name)

    else:
        canonical = entity_name

    return {

        "name": canonical,

        "type": entity_type,

        "original_name": entity_name,

        "resolved": canonical != entity_name

    }


# ==========================================================
# Resolve Entity List
# ==========================================================

def resolve_entities(entity_list):
    """
    Resolve a list of extracted entities.
    """

    resolved_entities = []

    seen = set()

    for entity_name, entity_type in entity_list:

        entity = resolve_entity(

            entity_name,

            entity_type

        )

        key = (

            entity["name"].lower(),

            entity["type"]

        )

        if key in seen:
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
    """

    grouped = {}

    for entity in entity_list:

        grouped.setdefault(

            entity["type"],

            []

        ).append(entity)

    return grouped


# ==========================================================
# Pretty Printer
# ==========================================================

def print_entities(entity_list):
    """
    Print grouped entities.
    """

    grouped = group_entities(entity_list)

    for entity_type in sorted(grouped):

        print("\n" + "=" * 60)

        print(entity_type)

        print("=" * 60)

        for entity in grouped[entity_type]:

            if entity["resolved"]:

                print(

                    f'{entity["original_name"]}'

                    f'  -->  '

                    f'{entity["name"]}'

                )

            else:

                print(entity["name"])


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    sample = [

        ("Indian Space Research Organisation", "ORGANIZATION"),

        ("ISRO", "ORGANIZATION"),

        ("Chandrayaan 3", "MISSION"),

        ("Chandrayaan-3", "MISSION"),

        ("PSLV-C62", "ROCKET_VARIANT"),

        ("LVM3", "LAUNCH_VEHICLE"),

        ("NASA", "ORGANIZATION"),

        ("National Aeronautics and Space Administration", "ORGANIZATION"),

        ("Vikram", "SPACECRAFT"),

        ("Pragyan", "SPACECRAFT"),

        ("Aditya L1", "MISSION")

    ]

    resolved = resolve_entities(sample)

    print_entities(resolved)