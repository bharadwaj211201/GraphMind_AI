from scrapers.domain_entities import *

# ==========================================================
# Entity Dictionary
# ==========================================================

ENTITY_TYPES = {}


def register_entities(entity_list, entity_type):
    """
    Register entities in lookup dictionary.
    """

    for entity in entity_list:
        ENTITY_TYPES[entity.lower().strip()] = entity_type


# ==========================================================
# Register All Entity Types
# ==========================================================

register_entities(MISSIONS, "MISSION")
register_entities(ORGANIZATIONS, "ORGANIZATION")
register_entities(CENTRES, "CENTRE")

register_entities(LAUNCH_VEHICLES, "LAUNCH_VEHICLE")
register_entities(ROCKET_VARIANTS, "ROCKET_VARIANT")

register_entities(SATELLITES, "SATELLITE")
register_entities(SPACECRAFT, "SPACECRAFT")

register_entities(PAYLOADS, "PAYLOAD")
register_entities(INSTRUMENTS, "INSTRUMENT")

register_entities(ASTRONAUTS, "ASTRONAUT")
register_entities(SCIENTISTS, "SCIENTIST")

register_entities(COUNTRIES, "COUNTRY")
register_entities(STATES, "STATE")
register_entities(CITIES, "CITY")

register_entities(SPACEPORTS, "SPACEPORT")
register_entities(FACILITIES, "FACILITY")
register_entities(LABORATORIES, "LABORATORY")

register_entities(PROGRAMS, "PROGRAM")

register_entities(TECHNOLOGIES, "TECHNOLOGY")

register_entities(CELESTIAL_BODIES, "CELESTIAL_BODY")


# ==========================================================
# Classify One Entity
# ==========================================================

def classify_entity(entity_name, current_type=None):
    """
    Return the canonical entity type.
    """

    key = entity_name.lower().strip()

    if key in ENTITY_TYPES:
        return ENTITY_TYPES[key]

    if current_type and current_type != "UNKNOWN":
        return current_type

    return "UNKNOWN"


# ==========================================================
# Classify Entity List
# ==========================================================

def classify_entities(entity_list):
    """
    Classify resolved entities.

    Input
    -----
    [
        {
            "name": "...",
            "type": "...",
            "original_name": "...",
            "resolved": True
        }
    ]

    Output
    ------
    Same structure with updated type.
    """

    classified = []

    seen = set()

    for entity in entity_list:

        entity_name = entity["name"]

        current_type = entity["type"]

        final_type = classify_entity(
            entity_name,
            current_type
        )

        entity["type"] = final_type

        key = (

            entity["name"].lower(),

            entity["type"]

        )

        if key in seen:
            continue

        seen.add(key)

        classified.append(entity)

    return classified


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    sample = [

        {
            "name": "ISRO",
            "type": "ORGANIZATION",
            "original_name": "Indian Space Research Organisation",
            "resolved": True
        },

        {
            "name": "Chandrayaan-3",
            "type": "MISSION",
            "original_name": "Chandrayaan 3",
            "resolved": True
        },

        {
            "name": "LVM3-M4",
            "type": "ROCKET_VARIANT",
            "original_name": "LVM3-M4",
            "resolved": False
        }

    ]

    classified = classify_entities(sample)

    from pprint import pprint

    pprint(classified)