import json

with open(
    "data/raw/isro/structured_missions.json",
    "r",
    encoding="utf-8"
) as f:

    records = json.load(f)

missions = set()
organizations = set()
vehicles = set()
centres = set()

for record in records:

    for entity_name, entity_type in record["custom_entities"]:

        if entity_type == "MISSION":
            missions.add(entity_name)

        elif entity_type == "ORG":
            organizations.add(entity_name)

        elif entity_type == "LAUNCH_VEHICLE":
            vehicles.add(entity_name)

        elif entity_type == "CENTRE":
            centres.add(entity_name)

print("\n" + "="*50)
print("ENTITY STATISTICS")
print("="*50)

print("MISSIONS         :", len(missions))
print("ORGANIZATIONS    :", len(organizations))
print("LAUNCH VEHICLES  :", len(vehicles))
print("CENTRES          :", len(centres))

total = (
    len(missions)
    + len(organizations)
    + len(vehicles)
    + len(centres)
)

print("-"*50)
print("TOTAL ENTITIES   :", total)

print("\nMISSIONS:")
for m in sorted(missions):
    print(" -", m)

print("\nORGANIZATIONS:")
for o in sorted(organizations):
    print(" -", o)

print("\nLAUNCH VEHICLES:")
for v in sorted(vehicles):
    print(" -", v)

print("\nCENTRES:")
for c in sorted(centres):
    print(" -", c)