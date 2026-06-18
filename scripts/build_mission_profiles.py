import json

with open(
    "data/raw/isro/structured_missions.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)

missions = {}

for record in data:

    for entity in record["custom_entities"]:

        name = entity[0]
        entity_type = entity[1]

        if entity_type != "MISSION":
            continue

        if name not in missions:

            missions[name] = {

                "organizations": set(),

                "launch_vehicles": set(),

                "urls": set()
            }

        missions[name]["organizations"].update(
            record["organizations"]
        )

        missions[name]["launch_vehicles"].update(
            record["launch_vehicles"]
        )

        missions[name]["urls"].add(
            record["url"]
        )

result = []

for mission, info in missions.items():

    result.append({

        "mission": mission,

        "organizations":
            list(info["organizations"]),

        "launch_vehicles":
            list(info["launch_vehicles"]),

        "urls":
            list(info["urls"])
    })

with open(
    "data/processed/mission_profiles/mission_profiles.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        indent=4,
        ensure_ascii=False
    )

print(
    "Mission Profiles Created:",
    len(result)
)