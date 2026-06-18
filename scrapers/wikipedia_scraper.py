import requests
from bs4 import BeautifulSoup


def scrape_wikipedia(url):

    try:

        print("Crawling:", url)

        headers = {
            "User-Agent": "Mozilla/5.0"
        }


        response = requests.get(
            url,
            headers=headers
        )


        if response.status_code != 200:
            return None



        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # Title
        title_tag = soup.find("h1")


        if title_tag:
            title = title_tag.text.strip()

        else:
            title = "Unknown"



        # Content
        paragraphs = soup.find_all("p")


        content = ""


        for p in paragraphs:

            content += p.text + " "



        if content.strip() == "":

            return None



        return {

            "title": title,

            "url": url,

            "content": content

        }



    except Exception as e:

        print("ERROR:",e)

        return None