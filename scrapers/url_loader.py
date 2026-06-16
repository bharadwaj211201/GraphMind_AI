# def load_url(filepath):
#     urls = []

#     with open(filepath, "r", encoding="utf-8") as f:
#         for line in f:
#             url = line.strip()

#             if url:
#                 urls.append(url)

#         return urls
    
# def get_mission_urls(urls):

#     keywords = [
#         # "mission",
#         "chandrayaan",
#         "gaganyaan",
#         "aditya",
#         "spadex",
#         "satellite",
#         "pslv",
#         "gslv",
#         "lvm3",
#         "nisar"
#     ]

#     mission_urls = []

#     for url in urls:
#         if any(
#             keyword.lower() in url.lower()
#             for keyword in keywords
#         ):
#             mission_urls.append(url)

#     return list(set(mission_urls))

def load_urls(filepath):

    urls = []

    with open(filepath, "r", encoding="utf-8") as f:

        for line in f:

            url = line.strip()

            if url:
                urls.append(url)

    return urls


def get_mission_urls(urls):

    keywords = [
        "mission",
        "chandrayaan",
        "gaganyaan",
        "aditya",
        "spadex",
        "satellite",
        "pslv",
        "gslv",
        "lvm3",
        "nisar"
    ]

    mission_urls = []

    for url in urls:

        url_lower = url.lower()

        # Skip PDFs
        if ".pdf" in url_lower:
            continue

        # Skip images
        if any(
            ext in url_lower
            for ext in [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".gif"
            ]
        ):
            continue

        # Skip media folder files
        if "/media_isro/" in url_lower:
            continue

        # Keep only mission-related URLs
        if any(
            keyword in url_lower
            for keyword in keywords
        ):
            mission_urls.append(url)

    return sorted(list(set(mission_urls)))