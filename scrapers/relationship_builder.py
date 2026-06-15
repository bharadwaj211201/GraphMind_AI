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
    
    return relationships