import requests
from bs4 import BeautifulSoup


def scrape_mission(url):

    response = requests.get(url)

    if response.status_code != 200:
        print("Failed:", url)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

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