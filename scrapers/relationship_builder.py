def create_relationships(record):

    relationships = []

    mission = record["mission_name"]

    for v in record["launch_vehicles"]:

        relationships.append(
            (
                mission,
                "USED",
                v
            )
        )
    
    for org in record["organizations"]:

        relationships.append(
            (
                mission,
                "INVOLVES",
                org
            )
        )
    
    for entity, label in record["custom_entities"]:
        if label == "CENTRE":
            relationships.append(
                (
                    mission,
                    "ASSOCIATED_WITH",
                    entity
                )
            )
        elif label == "MISSION":

            if entity.lower() != mission.lower():
                relationships.append(
                    (
                        mission,
                        "REFERENCES",
                        entity
                    )
                )

        elif label == "ORG":
            if entity not in record["organizations"]:
                relationships.append(
                    (
                        mission,
                        "COLLABORATES_WITH",
                        entity
                    )
                )
        
    
    return relationships