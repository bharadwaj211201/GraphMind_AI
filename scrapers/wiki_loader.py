import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def crawl_wikipedia(start_url, limit=50):


    visited = set()

    queue = [start_url]


    headers = {
        "User-Agent": "Mozilla/5.0"
    }



    while queue and len(visited) < limit:


        url = queue.pop(0)


        if url in visited:
            continue



        print("Crawling:", url)


        visited.add(url)



        try:


            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )


            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )



            for a in soup.find_all("a", href=True):


                href = a["href"]



                if href.startswith("/wiki/"):


                    if ":" in href:
                        continue



                    full_url = urljoin(
                        "https://en.wikipedia.org",
                        href
                    )



                    if full_url not in visited:

                        queue.append(full_url)



        except Exception as e:

            print("ERROR:",e)



    return list(visited)