import re
<<<<<<< HEAD
from scrapers.isro_entities import *
=======
from scrapers.domain_entities import *
>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e

LAUNCH_VEHICLES = [
    "PSLV",
    "GSLV",
    "LVM3",
    "SSLV"
]


def extract_entities(text):

    entities = []


    doc = nlp(text)


    for ent in doc.ents:


        if ent.label_ in [
            "ORG",
            "GPE",
            "PERSON",
            "DATE",
            "PRODUCT",
            "EVENT"
        ]:


            entities.append(
                (
                    ent.text,
                    ent.label_
                )
            )


    for mission in MISSIONS:

        if mission.lower() in text.lower():

            entities.append(
                (
                    mission,
                    "MISSION"
                )
            )


    for vehicle in LAUNCH_VEHICLES:

        if vehicle.lower() in text.lower():

            entities.append(
                (
                    vehicle,
                    "LAUNCH_VEHICLE"
                )
            )



    return list(set(entities))