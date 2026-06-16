# import requests
# from bs4 import BeautifulSoup


# def scrape_mission(url):
#     try:
#         response = requests.get(url, timeout=20)
#         if response.status_code != 200:
#             print(f"Failed ({response.status_code}) : {url}")
#             return None
#     except Exception as e:
#         print(f"Error scraping {url}")
#         print(e)
#         return None

#     if response.status_code != 200:
#         print("Failed:", url)
#         return None

#     soup = BeautifulSoup(response.text, "html.parser")

#     title = soup.title.text.strip()

#     text = soup.get_text(
#         separator=" ",
#         strip=True
#     )

#     mission_data = {
#         "url": url,
#         "title": title,
#         "content": text
#     }

#     return mission_data

import requests
from bs4 import BeautifulSoup


def scrape_mission(url):

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:

            print(
                f"Failed ({response.status_code}) : {url}"
            )

            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Some URLs are PDFs, redirects, media files, etc.
        if soup.title is None:

            print(
                f"No title found : {url}"
            )

            return None

        title = soup.title.text.strip()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        mission_data = {
            "url": url,
            "title": title,
            "content": text
        }

        return mission_data

    except Exception as e:

        print(
            f"Error scraping: {url}"
        )

        print(e)

        return None