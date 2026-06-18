import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://en.wikipedia.org"


KEYWORDS = [

    "isro",
    "space",
    "satellite",
    "rocket",
    "mission",
    "chandrayaan",
    "gaganyaan",
    "aditya",
    "pslv",
    "gslv",
    "lvm3",
    "vikram",
    "sarabhai",
    "dhawan",
    "department_of_space"

]


def crawl_isro_pages():


    start_url = (
        "https://en.wikipedia.org/wiki/"
        "Indian_Space_Research_Organisation"
    )


    visited = set()

    queue = [start_url]


    while queue and len(visited) < 100:


        url = queue.pop(0)



        if url in visited:
            continue



        print(
            "Crawling:",
            url
        )


        visited.add(url)



        try:


            response = requests.get(
                url,
                timeout=10
            )


            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )



            links = soup.find_all(
                "a",
                href=True
            )



            for link in links:


                href = link["href"]



                if href.startswith("/wiki/"):



                    if ":" in href:
                        continue



                    full_url = urljoin(
                        BASE_URL,
                        href
                    )



                    text = (
                        link.text
                        +
                        full_url
                    ).lower()



                    if any(
                        keyword in text
                        for keyword in KEYWORDS
                    ):



                        if (
                            full_url not in visited
                            and
                            full_url not in queue
                        ):

                            queue.append(
                                full_url
                            )



        except Exception as e:


            print(
                "Error:",
                e
            )



    return list(visited)