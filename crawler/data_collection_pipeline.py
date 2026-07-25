import json
import time
import warnings
import requests
import spacy

from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import deque

from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
from bs4 import ParserRejectedMarkup

warnings.filterwarnings(
    "ignore",
    category=XMLParsedAsHTMLWarning
)

# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_URL = "https://www.isro.gov.in"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64)"
    )
}

TIMEOUT = 15
MAX_RETRY = 3

RAW_DIR = Path("data/raw")
CATEGORY_DIR = RAW_DIR / "url_categories"
SCRAPED_DIR = RAW_DIR / "scraped"
MERGED_DIR = Path("data/merged")

RAW_DIR.mkdir(parents=True, exist_ok=True)
CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
SCRAPED_DIR.mkdir(parents=True, exist_ok=True)
MERGED_DIR.mkdir(parents=True, exist_ok=True)

LINK_FILE = RAW_DIR / "isro_links.txt"
FAILED_URL_FILE = RAW_DIR / "failed_urls.txt"

nlp = spacy.load("en_core_web_sm")

# ==========================================================
# COMMON HELPERS
# ==========================================================

def normalize_url(url):

    url = url.split("#")[0].strip()

    if url.endswith("/"):
        url = url[:-1]

    return url


def is_valid(url):

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if "isro.gov.in" not in parsed.netloc.lower():
        return False

    blocked = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".css",
        ".js",
        ".ico",
        ".pdf",
        ".zip",
        ".rar",
        ".7z",
        ".mp4",
        ".mp3",
        ".avi",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".xml",
        ".rss"
    )

    return not parsed.path.lower().endswith(blocked)


def save_failed_url(url):

    with open(
        FAILED_URL_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(url + "\n")


def safe_request(url):

    for attempt in range(MAX_RETRY):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                return response

        except requests.exceptions.RequestException:
            pass

        time.sleep(1)

    save_failed_url(url)

    return None


# ==========================================================
# LINK EXTRACTION
# ==========================================================

def get_links(url):

    response = safe_request(url)

    if response is None:
        return []

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    if (
        "html" not in content_type
        and "text" not in content_type
    ):
        return []

    try:

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

    except ParserRejectedMarkup:

        return []

    except Exception:

        return []

    links = set()

    for tag in soup.find_all("a", href=True):

        href = tag["href"].strip()

        if href.startswith(
            (
                "#",
                "mailto:",
                "javascript:",
                "tel:"
            )
        ):
            continue

        full = urljoin(url, href)

        full = normalize_url(full)

        if not is_valid(full):
            continue

        links.add(full)

    return sorted(links)


# ==========================================================
# WEBSITE CRAWLER
# ==========================================================

def crawl():

    discovered = set()

    visited = set()

    queue = deque([BASE_URL])

    discovered.add(BASE_URL)

    while queue:

        current = queue.popleft()

        if current in visited:
            continue

        visited.add(current)

        for link in get_links(current):

            if link not in discovered:

                discovered.add(link)

                queue.append(link)

        if len(visited) % 100 == 0:

            print(

                f"Visited : {len(visited):5d}"

                f" | Found : {len(discovered):5d}"

                f" | Queue : {len(queue):5d}"

            )

        if len(visited) % 500 == 0:

            with open(
                LINK_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                for item in sorted(discovered):
                    file.write(item + "\n")

    with open(
        LINK_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for item in sorted(discovered):
            file.write(item + "\n")

    print()
    print("=" * 60)
    print("Website Crawling Completed")
    print("Total URLs :", len(discovered))
    print("Saved :", LINK_FILE)
    print("=" * 60)

# ==========================================================
# URL CLASSIFICATION
# ==========================================================

CATEGORIES = {

    "missions": [
        "mission",
        "chandrayaan",
        "gaganyaan",
        "aditya",
        "spadex",
        "nisar",
        "mangalyaan"
    ],

    "launch_vehicles": [
        "pslv",
        "gslv",
        "sslv",
        "lvm3",
        "launch"
    ],

    "satellites": [
        "satellite",
        "insat",
        "cartosat",
        "resourcesat",
        "oceansat",
        "gsat",
        "risat",
        "hyisis"
    ],

    "spacecraft": [
        "spacecraft"
    ],

    "centres": [
        "centre",
        "center",
        "vssc",
        "sac",
        "shar",
        "istrac",
        "iirs"
    ],

    "science": [
        "science",
        "solar",
        "moon",
        "mars",
        "sun",
        "space"
    ],

    "technology": [
        "technology",
        "cryogenic",
        "propulsion",
        "navigation"
    ],

    "press_releases": [
        "press",
        "announcement",
        "update",
        "media"
    ]

}


def classify_urls():

    with open(
        LINK_FILE,
        encoding="utf-8"
    ) as file:

        urls = sorted(set(

            line.strip()

            for line in file

            if line.strip()

        ))

    classified = {

        category: []

        for category in CATEGORIES

    }

    classified["others"] = []

    for url in urls:

        lower = url.lower()

        matched = False

        for category, keywords in CATEGORIES.items():

            if any(

                keyword in lower

                for keyword in keywords

            ):

                classified[category].append(url)

                matched = True

                break

        if not matched:

            classified["others"].append(url)

    for category, links in classified.items():

        output = CATEGORY_DIR / f"{category}.txt"

        with open(

            output,

            "w",

            encoding="utf-8"

        ) as file:

            for link in sorted(set(links)):

                file.write(link + "\n")

        print(

            f"{category:<20}"

            f"{len(links)}"

        )


# ==========================================================
# PAGE SCRAPER
# ==========================================================

def scrape_page(url):

    response = safe_request(url)

    if response is None:

        return None

    content_type = response.headers.get(

        "Content-Type",

        ""

    ).lower()

    if (

        "html" not in content_type

        and "text" not in content_type

    ):

        return None

    try:

        soup = BeautifulSoup(

            response.text,

            "html.parser"

        )

    except ParserRejectedMarkup:

        return None

    except Exception:

        return None

    title = ""

    if soup.title:

        title = soup.title.get_text(

            strip=True

        )

    text = soup.get_text(

        separator=" ",

        strip=True

    )

    text = " ".join(text.split())

    if len(text) < 100:

        return None

    return {

        "url": url,

        "title": title,

        "content": text

    }


# ==========================================================
# BULK SCRAPER
# ==========================================================

def bulk_scrape():

    output = SCRAPED_DIR / "all_scraped_documents.json"

    documents = []

    scraped_urls = set()

    # -----------------------------
    # Resume support
    # -----------------------------

    if output.exists():

        try:

            with open(

                output,

                encoding="utf-8"

            ) as file:

                documents = json.load(file)

            scraped_urls = {

                item["url"]

                for item in documents

            }

            print()

            print(

                f"Resuming..."

                f" {len(scraped_urls)} pages already scraped."

            )

        except Exception:

            documents = []

            scraped_urls = set()

    # -----------------------------

    for txt_file in sorted(

        CATEGORY_DIR.glob("*.txt")

    ):

        category = txt_file.stem

        print()

        print(category)

        with open(

            txt_file,

            encoding="utf-8"

        ) as file:

            urls = [

                line.strip()

                for line in file

                if line.strip()

            ]

        count = 0

        for url in urls:

            if url in scraped_urls:

                continue

            page = scrape_page(url)

            if page is None:

                continue

            page["category"] = category

            documents.append(page)

            scraped_urls.add(url)

            count += 1

            if count % 25 == 0:

                print(

                    f"{count} pages scraped"

                )

                with open(

                    output,

                    "w",

                    encoding="utf-8"

                ) as file:

                    json.dump(

                        documents,

                        file,

                        indent=4,

                        ensure_ascii=False

                    )

            time.sleep(0.2)

    with open(

        output,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            documents,

            file,

            indent=4,

            ensure_ascii=False

        )

    print()

    print("=" * 60)

    print(

        "Documents Scraped :",

        len(documents)

    )

    print(

        "Saved To :",

        output

    )

    print("=" * 60)

# ==========================================================
# ENTITY EXTRACTION
# ==========================================================

def extract_entities():

    input_file = SCRAPED_DIR / "all_scraped_documents.json"
    output_file = SCRAPED_DIR / "all_scraped_entities.json"

    if not input_file.exists():

        print("Scraped documents not found.")
        return

    with open(
        input_file,
        encoding="utf-8"
    ) as file:

        documents = json.load(file)

    records = []
    processed_urls = set()

    # ------------------------------------------------------
    # Resume Support
    # ------------------------------------------------------

    if output_file.exists():

        try:

            with open(
                output_file,
                encoding="utf-8"
            ) as file:

                records = json.load(file)

            processed_urls = {

                record["url"]

                for record in records

            }

            print()
            print(
                f"Resuming entity extraction..."
                f" {len(processed_urls)} already processed."
            )

        except Exception:

            records = []
            processed_urls = set()

    # ------------------------------------------------------

    count = len(processed_urls)

    for document in documents:

        if document["url"] in processed_urls:
            continue

        text = document.get("content", "")

        try:

            doc = nlp(text[:100000])

        except Exception:

            continue

        entities = []
        seen = set()

        for ent in doc.ents:

            key = (

                ent.text.strip(),

                ent.label_

            )

            if key not in seen:

                seen.add(key)

                entities.append({

                    "text": ent.text.strip(),

                    "label": ent.label_

                })

        records.append({

            "title": document["title"],

            "url": document["url"],

            "category": document["category"],

            "entities": entities

        })

        processed_urls.add(document["url"])

        count += 1

        if count % 25 == 0:

            print(f"{count} documents processed")

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    records,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("Entity Records :", len(records))
    print("Saved :", output_file)
    print("=" * 60)


# ==========================================================
# BUILD WEBSITE DATASET
# ==========================================================

def build_website_entities():

    input_file = SCRAPED_DIR / "all_scraped_entities.json"
    output_file = MERGED_DIR / "website_entities.json"

    if not input_file.exists():

        print("Entity file not found.")
        return

    with open(
        input_file,
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    website = []

    seen = set()

    for record in records:

        if record["url"] in seen:
            continue

        seen.add(record["url"])

        website.append({

            "mission": record["title"],

            "category": record["category"],

            "url": record["url"],

            "entities": record["entities"],

            "source": "ISRO Website"

        })

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            website,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("Website Records :", len(website))
    print("Saved :", output_file)
    print("=" * 60)


# ==========================================================
# BUILD UNIFIED KNOWLEDGE BASE
# ==========================================================

def build_unified_kb():

    website_file = MERGED_DIR / "website_entities.json"
    output_file = MERGED_DIR / "unified_knowledge_base.json"

    records = []

    seen = set()

    if website_file.exists():

        with open(
            website_file,
            encoding="utf-8"
        ) as file:

            website_records = json.load(file)

        for item in website_records:

            if item["url"] in seen:
                continue

            seen.add(item["url"])
            records.append(item)

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("Unified Records :", len(records))
    print("Saved :", output_file)
    print("=" * 60)

# ==========================================================
# MAIN
# ==========================================================

def main():

    print()
    print("=" * 70)
    print("GRAPHMIND AI - DATA COLLECTION PIPELINE")
    print("=" * 70)

    # ------------------------------------------------------
    # Change this number if you want to resume
    #
    # 1 = Crawl Website
    # 2 = URL Classification
    # 3 = Bulk Scraping
    # 4 = Entity Extraction
    # 5 = Website Dataset
    # 6 = Unified Knowledge Base
    # ------------------------------------------------------

    START_STAGE = 1

    # ------------------------------------------------------

    if START_STAGE <= 1:

        print("\nSTAGE 1 : WEBSITE CRAWLING\n")

        crawl()

    else:

        print("\nSkipping Stage 1")

    # ------------------------------------------------------

    if START_STAGE <= 2:

        print("\nSTAGE 2 : URL CLASSIFICATION\n")

        classify_urls()

    else:

        print("\nSkipping Stage 2")

    # ------------------------------------------------------

    if START_STAGE <= 3:

        print("\nSTAGE 3 : BULK SCRAPING\n")

        bulk_scrape()

    else:

        print("\nSkipping Stage 3")

    # ------------------------------------------------------

    if START_STAGE <= 4:

        print("\nSTAGE 4 : ENTITY EXTRACTION\n")

        extract_entities()

    else:

        print("\nSkipping Stage 4")

    # ------------------------------------------------------

    if START_STAGE <= 5:

        print("\nSTAGE 5 : BUILD WEBSITE DATASET\n")

        build_website_entities()

    else:

        print("\nSkipping Stage 5")

    # ------------------------------------------------------

    if START_STAGE <= 6:

        print("\nSTAGE 6 : BUILD UNIFIED KNOWLEDGE BASE\n")

        build_unified_kb()

    else:

        print("\nSkipping Stage 6")

    print()
    print("=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print()
    print("Generated Files")
    print("-" * 40)

    files = [

        LINK_FILE,

        CATEGORY_DIR,

        SCRAPED_DIR / "all_scraped_documents.json",

        SCRAPED_DIR / "all_scraped_entities.json",

        MERGED_DIR / "website_entities.json",

        MERGED_DIR / "unified_knowledge_base.json"

    ]

    for item in files:

        if item.exists():

            print("[OK] ", item)

        else:

            print("[--] ", item)


# ==========================================================
# DRIVER
# ==========================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print("\n\nPipeline stopped by user.")

    except Exception as e:

        print("\nPipeline crashed.")
        print(type(e).__name__)
        print(e)