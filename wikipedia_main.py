import json
import os

from scrapers.wiki_loader import crawl_wikipedia
from scrapers.wikipedia_scraper import scrape_wikipedia
from scrapers.entity_extractor import extract_entities


start_url = "https://en.wikipedia.org/wiki/Indian_Space_Research_Organisation"


wiki_urls = crawl_wikipedia(
    start_url,
    limit=50
)


print(wiki_urls[:10])

print(
    "\nTotal Wikipedia URLs Found:",
    len(wiki_urls)
)


records = []


for url in wiki_urls:

    data = scrape_wikipedia(url)

    if data:
        records.append(data)


print(
    "\nSaved Wikipedia Pages:",
    len(records)
)


os.makedirs(
    "data/raw/wikipedia",
    exist_ok=True
)


with open(
    "data/raw/wikipedia/wikipedia_pages.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        records,
        f,
        indent=4,
        ensure_ascii=False
    )


all_entities = []


print("\n")
print("="*50)
print("ENTITIES")
print("="*50)


for page in records:

    print(
        "\n",
        page["title"]
    )


    entities = extract_entities(
        page["content"]
    )


    all_entities.append(
        {
            "page": page["title"],
            "url": page["url"],
            "entities": entities
        }
    )


    for e in entities:
        print(e)



with open(
    "data/raw/wikipedia/wikipedia_entities.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_entities,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\nWikipedia raw data saved")
print("Wikipedia entities saved")