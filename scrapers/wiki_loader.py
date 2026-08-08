"""
wiki_loader.py

Search Wikipedia pages for ISRO entities.

Uses the official Wikipedia REST API.
"""

import requests
from urllib.parse import quote

# ==========================================================
# Configuration
# ==========================================================

HEADERS = {
    "User-Agent": "ISRO-KnowledgeGraph/1.0 (Educational Project)",
    "Accept": "application/json",
    "Accept-Language": "en"
}

REST_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"


# ==========================================================
# Search Single Page
# ==========================================================

def search_wikipedia(title):
    """
    Search a Wikipedia page using the REST API.

    Parameters
    ----------
    title : str

    Returns
    -------
    str | None
        Canonical Wikipedia URL if found.
    """

    encoded_title = quote(title)

    url = REST_API + encoded_title

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        # Missing article
        if data.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
            return None

        # Canonical URL
        if "content_urls" in data:

            desktop = data["content_urls"].get("desktop", {})

            if "page" in desktop:
                return desktop["page"]

        return None

    except Exception as e:

        print(f"[ERROR] {title} : {e}")

        return None


# ==========================================================
# Search Multiple Pages
# ==========================================================

def search_multiple(titles):
    """
    Search multiple Wikipedia pages.

    Parameters
    ----------
    titles : list

    Returns
    -------
    dict
    """

    results = {}

    print()

    for title in titles:

        print(f"Searching : {title}")

        url = search_wikipedia(title)

        if url:

            print("   [FOUND]")

            results[title] = url

        else:

            print("   [NOT FOUND]")


    return results


# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    pages = search_multiple([
        "Chandrayaan-3",
        "Aditya-L1",
        "PSLV",
        "Gaganyaan"
    ])

    print()

    for key, value in pages.items():

        print(key)

        print(value)

        print()