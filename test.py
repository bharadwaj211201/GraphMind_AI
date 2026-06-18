# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# url = "https://www.isro.gov.in"

# response = requests.get(url)

# print(response.status_code)

# soup = BeautifulSoup(response.text,"html.parser")

# print(soup.title.text)
# print(response.text[:3000])

# for link in soup.find_all("a", href=True):
#     print(urljoin(url, link["href"]))

# import spacy

# nlp = spacy.load("en_core_web_sm")

# doc = nlp(
#     "NASA and ISRO launched NISAR using GSLV-F16."
# )

# for ent in doc.ents:
#     print(ent.text, ent.label_)

# from scrapers.isro_entities import *

# def extract_custom_entities(text):

#     entities = []

#     for m in MISSIONS:
#         if m.lower() in text.lower():
#             entities.append((m, "MISSION"))

#     for v in LAUNCH_VEHICLES:
#         if v.lower() in text.lower():
#             entities.append((v, "LAUNCH_VEHICLE"))

#     for org in ORGANIZATIONS:
#         if org.lower() in text.lower():
#             entities.append(
#                 (org, "ORG")
#             )

#     return entities


# text = """

# NASA and ISRO launched NISAR
# using GSLV-F16

# """

# print(extract_custom_entities(text))

# import requests

# response = requests.get("https://isro.gov.in")

# print(response.status_code)

<<<<<<< HEAD
import requests

response = requests.get("https://www.google.com")

print(response.status_code)
=======
# import requests

# response = requests.get("https://www.google.com")

# print(response.status_code)
>>>>>>> dfcadb51a4ff8454f805f4df269812c61c35b60e
