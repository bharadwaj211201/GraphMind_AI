def create_relationships(record):
    """
    Create Knowledge Graph relationships from a document.

    Input:
        record = {
            "title": "...",
            "entities": [...]
        }

    Returns:
        List of triples:
        (subject, relationship, object)
    """

    relationships = []

    document = record["title"]

    entities = record["entities"]

    # =====================================================
    # Group entities by type
    # =====================================================

    entity_dict = {}

    for entity in entities:

        entity_name = entity["name"]

        entity_type = entity["type"]

        entity_dict.setdefault(
            entity_type,
            []
        ).append(entity_name)

    # =====================================================
    # Document -> Mission
    # =====================================================

    for mission in entity_dict.get("MISSION", []):

        relationships.append(
            (
                document,
                "ABOUT_MISSION",
                mission
            )
        )

        # ---------------------------------------------

        for org in entity_dict.get("ORGANIZATION", []):

            relationships.append(
                (
                    mission,
                    "DEVELOPED_BY",
                    org
                )
            )

        # ---------------------------------------------

        for centre in entity_dict.get("CENTRE", []):

            relationships.append(
                (
                    mission,
                    "MANAGED_BY",
                    centre
                )
            )

        # ---------------------------------------------

        for vehicle in entity_dict.get("LAUNCH_VEHICLE", []):

            relationships.append(
                (
                    mission,
                    "LAUNCHED_BY",
                    vehicle
                )
            )

        for variant in entity_dict.get("ROCKET_VARIANT", []):

            relationships.append(
                (
                    mission,
                    "LAUNCHED_BY",
                    variant
                )
            )

        # ---------------------------------------------

        for satellite in entity_dict.get("SATELLITE", []):

            relationships.append(
                (
                    mission,
                    "HAS_SATELLITE",
                    satellite
                )
            )

        # ---------------------------------------------

        for spacecraft in entity_dict.get("SPACECRAFT", []):

            relationships.append(
                (
                    mission,
                    "HAS_SPACECRAFT",
                    spacecraft
                )
            )

        # ---------------------------------------------

        for payload in entity_dict.get("PAYLOAD", []):

            relationships.append(
                (
                    mission,
                    "HAS_PAYLOAD",
                    payload
                )
            )

        # ---------------------------------------------

        for instrument in entity_dict.get("INSTRUMENT", []):

            relationships.append(
                (
                    mission,
                    "HAS_INSTRUMENT",
                    instrument
                )
            )

        # ---------------------------------------------

        for astronaut in entity_dict.get("ASTRONAUT", []):

            relationships.append(
                (
                    mission,
                    "INVOLVES_ASTRONAUT",
                    astronaut
                )
            )

        # ---------------------------------------------

        for scientist in entity_dict.get("SCIENTIST", []):

            relationships.append(
                (
                    mission,
                    "MENTIONS_SCIENTIST",
                    scientist
                )
            )

        # ---------------------------------------------

        for country in entity_dict.get("COUNTRY", []):

            relationships.append(
                (
                    mission,
                    "ASSOCIATED_WITH",
                    country
                )
            )

        # ---------------------------------------------

        for state in entity_dict.get("STATE", []):

            relationships.append(
                (
                    mission,
                    "ASSOCIATED_WITH",
                    state
                )
            )

        for city in entity_dict.get("CITY", []):

            relationships.append(
                (
                    mission,
                    "ASSOCIATED_WITH",
                    city
                )
            )

        # ---------------------------------------------

        for spaceport in entity_dict.get("SPACEPORT", []):

            relationships.append(
                (
                    mission,
                    "LAUNCHED_FROM",
                    spaceport
                )
            )

        # ---------------------------------------------

        for facility in entity_dict.get("FACILITY", []):

            relationships.append(
                (
                    mission,
                    "USES_FACILITY",
                    facility
                )
            )

        # ---------------------------------------------

        for laboratory in entity_dict.get("LABORATORY", []):

            relationships.append(
                (
                    mission,
                    "USES_LABORATORY",
                    laboratory
                )
            )

        # ---------------------------------------------

        for technology in entity_dict.get("TECHNOLOGY", []):

            relationships.append(
                (
                    mission,
                    "USES_TECHNOLOGY",
                    technology
                )
            )

        # ---------------------------------------------

        for body in entity_dict.get("CELESTIAL_BODY", []):

            relationships.append(
                (
                    mission,
                    "TARGETS",
                    body
                )
            )

        # ---------------------------------------------

        for program in entity_dict.get("PROGRAM", []):

            relationships.append(
                (
                    mission,
                    "PART_OF_PROGRAM",
                    program
                )
            )

    # =====================================================
    # Organization Collaboration
    # =====================================================

    organizations = entity_dict.get(
        "ORGANIZATION",
        []
    )

    for i in range(len(organizations)):

        for j in range(i + 1, len(organizations)):

            relationships.append(
                (
                    organizations[i],
                    "COLLABORATES_WITH",
                    organizations[j]
                )
            )

    # =====================================================
    # Remove duplicate relationships
    # =====================================================

    return list(set(relationships)) 