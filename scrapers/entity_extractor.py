import spacy

from scrapers.isro_entities import *


nlp = spacy.load(
    "en_core_web_sm"
)


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