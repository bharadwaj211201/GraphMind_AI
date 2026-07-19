"""
Knowledge Graph Document Classifier
-----------------------------------
Classifies every ISRO document into a richer document taxonomy.
"""


def contains_any(text, keywords):
    return any(word in text for word in keywords)


def classify_document(title, url=""):

    title = title.lower()
    url = url.lower()

    text = title + " " + url

    # ======================================================
    # Mission Home Pages
    # ======================================================

    if (
        "mission_" in url
        or "/mission" in url
        or "mission home" in title
    ):
        return "MISSION_PAGE"

    # ======================================================
    # Launch Campaigns
    # ======================================================

    launch_keywords = [
        "launch",
        "lift off",
        "liftoff",
        "launch campaign",
        "launching",
        "launch vehicle"
    ]

    if contains_any(text, launch_keywords):
        return "LAUNCH_CAMPAIGN"

    # ======================================================
    # Rocket / Vehicle
    # ======================================================

    rocket_keywords = [
        "pslv",
        "gslv",
        "lvm3",
        "sslv",
        "cryogenic",
        "booster",
        "stage"
    ]

    if contains_any(text, rocket_keywords):
        return "LAUNCH_VEHICLE"

    # ======================================================
    # Flight Test
    # ======================================================

    flight_keywords = [
        "test",
        "hot test",
        "engine test",
        "air drop",
        "qualification",
        "flight test",
        "crew escape",
        "tv-d",
        "abort"
    ]

    if contains_any(text, flight_keywords):
        return "FLIGHT_TEST"

    # ======================================================
    # Mission Updates
    # ======================================================

    update_keywords = [
        "update",
        "achievement",
        "successful",
        "accomplished",
        "milestone",
        "completed",
        "returns",
        "return",
        "landed",
        "undocking",
        "docking"
    ]

    if contains_any(text, update_keywords):
        return "MISSION_UPDATE"

    # ======================================================
    # Scientific Results
    # ======================================================

    science_keywords = [
        "study",
        "research",
        "science",
        "measurement",
        "observe",
        "observes",
        "observation",
        "observations",
        "reveals",
        "finding",
        "solar",
        "magnetic",
        "plasma",
        "radiation",
        "journal"
    ]

    if contains_any(text, science_keywords):
        return "SCIENTIFIC_RESULT"

    # ======================================================
    # Payload Documents
    # ======================================================

    payload_keywords = [
        "payload",
        "instrument",
        "spectrometer",
        "camera",
        "radar",
        "sensor",
        "telescope"
    ]

    if contains_any(text, payload_keywords):
        return "PAYLOAD_DOCUMENT"

    # ======================================================
    # Technical Documents
    # ======================================================

    technical_keywords = [
        "design",
        "technical",
        "configuration",
        "architecture",
        "system",
        "specification"
    ]

    if contains_any(text, technical_keywords):
        return "TECHNICAL_DOCUMENT"

    # ======================================================
    # Collaboration
    # ======================================================

    collaboration_keywords = [
        "collaboration",
        "joint",
        "agreement",
        "partner",
        "cooperation",
        "nasa",
        "esa",
        "jaxa"
    ]

    if contains_any(text, collaboration_keywords):
        return "COLLABORATION"

    # ======================================================
    # Announcement
    # ======================================================

    announcement_keywords = [
        "announcement",
        "opportunity",
        "ao",
        "invitation",
        "call for"
    ]

    if contains_any(text, announcement_keywords):
        return "ANNOUNCEMENT"

    # ======================================================
    # Brochure
    # ======================================================

    if "brochure" in text:
        return "BROCHURE"

    # ======================================================
    # Annual Report
    # ======================================================

    if "annual report" in text:
        return "ANNUAL_REPORT"

    # ======================================================
    # Press Release
    # ======================================================

    if contains_any(text, [
        "press",
        "media",
        "release"
    ]):
        return "PRESS_RELEASE"

    # ======================================================
    # Event
    # ======================================================

    if contains_any(text, [
        "conference",
        "workshop",
        "symposium",
        "expo",
        "glex"
    ]):
        return "EVENT"

    # ======================================================
    # Default
    # ======================================================

    return "NEWS"