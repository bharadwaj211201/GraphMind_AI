import ollama

MODEL = "llama3.2:3b"


def get_intent(question):

    prompt = f"""
You are an AI Intent Classifier.

Your job is to classify user questions into ONE of these intents.

Return ONLY ONE WORD.

Possible intents:

mission
organization
person
location
date
comparison
list_missions
list_organizations
list_people
list_locations
list_dates
unknown

Examples

Tell me about Chandrayaan-3
mission

Tell me about Aditya-L1
mission

Tell me about SpaDeX
mission

Who worked on Chandrayaan-3
person

Who developed Aditya-L1
person

Which organizations worked on Chandrayaan-3
organization

Where was Chandrayaan-3 launched
location

When was Chandrayaan-3 launched
date

Compare Chandrayaan-2 and Chandrayaan-3
comparison

Difference between PSLV and GSLV
comparison

List all missions
list_missions

Show all ISRO missions
list_missions

List organizations
list_organizations

Show scientists
list_people

List locations
list_locations

List dates
list_dates

Question

{question}

Intent:
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip().lower()