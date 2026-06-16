import re
from scrapers.isro_entities import *

LAUNCH_VEHICLES = [
    "PSLV",
    "GSLV",
    "LVM3",
    "SSLV"
]

ORGANIZATIONS = [
    "ISRO",
    "NASA",
    "ESA",
    "JAXA",
    "NSIL"
]

def extract_launch_vehicle(text):


    found = []

    for i in LAUNCH_VEHICLES:
        if i.lower() in text.lower():
            found.append(i)

    return list(set(found))

def extract_organizations(text):
    found = []

    for org in ORGANIZATIONS:

        if org.lower() in text.lower():
            found.append(org)

    return list(set(found))

def extract_custom_entities(text):

    entities = []

    for mission in MISSIONS:

        if mission.lower() in text.lower():
            entities.append(
                (mission, "MISSION")
            )

    for vehicle in LAUNCH_VEHICLES:

        if vehicle.lower() in text.lower():
            entities.append(
                (vehicle, "LAUNCH_VEHICLE")
            )

    for org in ORGANIZATIONS:

        if org.lower() in text.lower():
            entities.append(
                (org, "ORG")
            )

    for centre in CENTRES:

        if centre.lower() in text.lower():
            entities.append(
                (centre, "CENTRE")
            )

    return entities