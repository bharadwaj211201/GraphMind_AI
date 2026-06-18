def classify_document(title):

    title = title.lower()

    if "press" in title:
        return "PRESS_RELEASE"

    if "study" in title:
        return "SCIENTIFIC_ARTICLE"

    if "observes" in title:
        return "SCIENTIFIC_ARTICLE"

    if "reveals" in title:
        return "SCIENTIFIC_ARTICLE"

    if "mission" in title:
        return "MISSION"

    return "NEWS"