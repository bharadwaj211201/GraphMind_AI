import json
import re
from collections import defaultdict

from scrapers.document_classifier import classify_document
from scrapers.domain_entities import MISSIONS

#=====================================================
# Load Documents
#=====================================================

def load_documents(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
    
# ==========================================================
# Mission Alias Dictionary
# ==========================================================

MISSION_ALIASES = {

    "Axiom-4": [
        "Axiom-4",
        "Ax-04",
        "Axiom Mission-04"
        "Axiom Mission 4"
    ],

    "Aditya-L1": [
        "Aditya-L1",
        "Aditya L1",
        "Solar Mission"
    ],

    "Chandrayaan-2": [
        "Chandrayaan-2",
        "Chandrayaan 2",
        "CH-2"
    ],

    "Chandrayaan-3": [
        "Chandrayaan-3",
        "Chandrayaan 3",
        "CH-3"
    ],

    "Mangalyaan": [
        "Mars Orbiter Mission",
        "Mangalyaan",
        "MOM"
    ],

    "NISAR": [
        "NISAR",
        "NASA-ISRO Synthetic Aperture Radar"
    ],

    "SpaDex": [
        "SpaDex",
        "SpaDeX"
    ],

    "Gaganyaan": [
        "Gaganyaan",
        "Human Space Flight"
    ]
}


# ==========================================================
# Document Type Weights
# ==========================================================

DOCUMENT_WEIGHTS = {

    "MISSION_PAGE": 50,

    "MISSION_UPDATE": 40,

    "SCIENTIFIC_RESULT": 30,

    "PRESS_RELEASE": 20,

    "COLLABORATION": 15,

    "TECHNICAL_DOCUMENT": 15,

    "PAYLOAD_DOCUMENT": 15,

    "BROCHURE": 10,

    "NEWS": 5
}


# ==========================================================
# Entity Mapping
# ==========================================================

ENTITY_MAPPING = {

    "ORGANIZATION": "organizations",

    "CENTRE": "centres",

    "LAUNCH_VEHICLE": "launch_vehicles",

    "ROCKET_VARIANT": "rocket_variants",

    "SATELLITE": "satellites",

    "SPACECRAFT": "spacecraft",

    "PAYLOAD": "payloads",

    "ASTRONAUT": "astronauts",

    "SCIENTIST": "scientists",

    "COUNTRY": "countries",

    "TECHNOLOGY": "technologies",

    "CELESTIAL_BODY": "celestial_bodies"
}


# ==========================================================
# Normalize Text
# ==========================================================

def normalize(text):

    text = text.lower()

    text = text.replace("-", "")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# Mission Candidate Generator
# ==========================================================

def get_candidate_missions(document):

    candidates = set()

    entities = document.get("custom_entities", [])

    title = document.get("mission_name", "")

    url = document.get("url", "")

    content = document.get("content", "")

    search_text = " ".join([title, url, content])

    search_text = normalize(search_text)

    # -----------------------------
    # MISSION entities
    # -----------------------------

    for entity_name, entity_type in entities:

        if entity_type == "MISSION":

            candidates.add(entity_name)

    # -----------------------------
    # Alias Search
    # -----------------------------

    for mission, aliases in MISSION_ALIASES.items():

        for alias in aliases:

            if normalize(alias) in search_text:

                candidates.add(mission)

                break

    # -----------------------------
    # Dictionary Search
    # -----------------------------

    for mission in MISSIONS:

        if normalize(mission) in search_text:

            candidates.add(mission)

    return sorted(candidates)


# ==========================================================
# Mission Detection Engine
# ==========================================================

def detect_primary_mission(document):

    title = normalize(
        document.get("mission_name", "")
    )

    url = normalize(
        document.get("url", "")
    )

    content = normalize(
        document.get("content", "")
    )

    document_type = classify_document(
        document.get("mission_name", ""),
        document.get("url", "")
    )

    candidates = get_candidate_missions(document)

    if not candidates:
        return None

    scores = {}

    for mission in candidates:

        score = 0

        reasons = []

        mission_key = normalize(mission)

        # ---------------------------------
        # Title Match
        # ---------------------------------

        if mission_key in title:

            score += 120

            reasons.append("TITLE")

        # ---------------------------------
        # URL Match
        # ---------------------------------

        if mission_key in url:

            score += 80

            reasons.append("URL")

        # ---------------------------------
        # Content Frequency
        # ---------------------------------

        frequency = content.count(mission_key)

        if frequency:

            score += frequency * 2

            reasons.append(
                f"CONTENT({frequency})"
            )

        # ---------------------------------
        # Document Type
        # ---------------------------------

        score += DOCUMENT_WEIGHTS.get(
            document_type,
            0
        )

        reasons.append(document_type)

        scores[mission] = {

            "score": score,

            "reason": reasons
        }

    best = max(

        scores.items(),

        key=lambda x: x[1]["score"]

    )

    return {

        "mission": best[0],

        "confidence": round(
            min(best[1]["score"] / 250, 1.0),
            2
        ),

        "reason": ", ".join(
            best[1]["reason"]
        )
    }

# ==========================================================
# Build Mission Profiles (Knowledge Fusion Engine)
# ==========================================================

def build_mission_profiles(documents):

    profiles = defaultdict(lambda: {

        "mission": "",

        "document_count": 0,

        "document_types": set(),

        "organizations": set(),

        "centres": set(),

        "launch_vehicles": set(),

        "rocket_variants": set(),

        "satellites": set(),

        "spacecraft": set(),

        "payloads": set(),

        "astronauts": set(),

        "scientists": set(),

        "countries": set(),

        "technologies": set(),

        "celestial_bodies": set(),

        "documents": [],

        "urls": set(),

        "sources": set(),

        "confidence_scores": [],

        "detection_reasons": []
    })

    # ======================================================
    # Process Every Document
    # ======================================================

    for document in documents:

        result = detect_primary_mission(document)

        if result is None:
            continue

        mission = result["mission"]

        profile = profiles[mission]

        profile["mission"] = mission

        profile["document_count"] += 1

        profile["documents"].append(
            document.get("mission_name", "")
        )

        profile["urls"].add(
            document.get("url", "")
        )

        profile["sources"].add(
            document.get("source", "Unknown")
        )

        profile["document_types"].add(

            classify_document(

                document.get("mission_name", ""),

                document.get("url", "")

            )

        )

        profile["confidence_scores"].append(
            result["confidence"]
        )

        profile["detection_reasons"].append(
            result["reason"]
        )

        # ==========================================
        # Merge Entities
        # ==========================================

        for entity_name, entity_type in document.get(
            "custom_entities",
            []
        ):

            if entity_type in ENTITY_MAPPING:

                profile[
                    ENTITY_MAPPING[entity_type]
                ].add(entity_name)

    # ======================================================
    # Final Formatting
    # ======================================================

    mission_profiles = []

    for profile in profiles.values():

        # Convert sets into sorted lists

        for key in list(profile.keys()):

            if isinstance(profile[key], set):

                profile[key] = sorted(profile[key])

        profile["documents"] = sorted(
            set(profile["documents"])
        )

        # Average Confidence

        if profile["confidence_scores"]:

            profile["average_confidence"] = round(

                sum(profile["confidence_scores"])

                /

                len(profile["confidence_scores"]),

                2

            )

        else:

            profile["average_confidence"] = 0

        # Remove temporary data

        del profile["confidence_scores"]

        profile["detection_reasons"] = sorted(

            set(profile["detection_reasons"])

        )

        mission_profiles.append(profile)

    # ======================================================
    # Sort by Number of Documents
    # ======================================================

    mission_profiles.sort(

        key=lambda x: (

            -x["document_count"],

            x["mission"]

        )

    )

    return mission_profiles

# ==========================================================
# Save Mission Profiles
# ==========================================================

def save_profiles(profiles, filepath):

    with open(filepath, "w", encoding="utf-8") as f:

        json.dump(
            profiles,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)
    print("MISSION PROFILE GENERATION COMPLETED")
    print("=" * 70)

    print(f"Mission Profiles Generated : {len(profiles)}")

    total_documents = sum(
        profile["document_count"]
        for profile in profiles
    )

    print(f"Documents Linked           : {total_documents}")

    if profiles:

        average_confidence = round(

            sum(
                profile["average_confidence"]
                for profile in profiles
            )

            /

            len(profiles),

            2

        )

    else:

        average_confidence = 0

    print(
        f"Average Confidence         : {average_confidence}"
    )

    print("\nMission Summary")

    print("-" * 70)

    for profile in profiles:

        print(

            f"{profile['mission']:<22}"

            f" Docs : {profile['document_count']:<3}"

            f" Confidence : {profile['average_confidence']}"

        )

    print("-" * 70)

    print(f"\nProfiles Saved To : {filepath}")


# ==========================================================
# Mission Statistics
# ==========================================================

def print_statistics(profiles):

    print("\n")

    print("=" * 70)
    print("MISSION PROFILE STATISTICS")
    print("=" * 70)

    total_documents = 0

    total_organizations = 0

    total_centres = 0

    total_launch_vehicles = 0

    total_rocket_variants = 0

    total_satellites = 0

    total_spacecraft = 0

    total_payloads = 0

    total_astronauts = 0

    total_scientists = 0

    total_countries = 0

    total_technologies = 0

    total_celestial_bodies = 0

    for profile in profiles:

        total_documents += profile["document_count"]

        total_organizations += len(
            profile["organizations"]
        )

        total_centres += len(
            profile["centres"]
        )

        total_launch_vehicles += len(
            profile["launch_vehicles"]
        )

        total_rocket_variants += len(
            profile["rocket_variants"]
        )

        total_satellites += len(
            profile["satellites"]
        )

        total_spacecraft += len(
            profile["spacecraft"]
        )

        total_payloads += len(
            profile["payloads"]
        )

        total_astronauts += len(
            profile["astronauts"]
        )

        total_scientists += len(
            profile["scientists"]
        )

        total_countries += len(
            profile["countries"]
        )

        total_technologies += len(
            profile["technologies"]
        )

        total_celestial_bodies += len(
            profile["celestial_bodies"]
        )

    print(f"Profiles             : {len(profiles)}")
    print(f"Documents            : {total_documents}")
    print(f"Organizations        : {total_organizations}")
    print(f"Centres              : {total_centres}")
    print(f"Launch Vehicles      : {total_launch_vehicles}")
    print(f"Rocket Variants      : {total_rocket_variants}")
    print(f"Satellites           : {total_satellites}")
    print(f"Spacecraft           : {total_spacecraft}")
    print(f"Payloads             : {total_payloads}")
    print(f"Astronauts           : {total_astronauts}")
    print(f"Scientists           : {total_scientists}")
    print(f"Countries            : {total_countries}")
    print(f"Technologies         : {total_technologies}")
    print(f"Celestial Bodies     : {total_celestial_bodies}")

    print("=" * 70)


# ==========================================================
# Validation
# ==========================================================

def validate_profiles(profiles):

    print("\n")

    print("=" * 70)
    print("MISSION PROFILE VALIDATION")
    print("=" * 70)

    valid_profiles = 0

    invalid_profiles = 0

    for profile in profiles:

        errors = []

        if not profile["mission"]:

            errors.append("Missing Mission")

        if profile["document_count"] == 0:

            errors.append("No Documents")

        if len(profile["documents"]) == 0:

            errors.append("Empty Documents")

        if len(profile["urls"]) == 0:

            errors.append("No URLs")

        if errors:

            invalid_profiles += 1

            print(f"\n❌ {profile['mission']}")

            for error in errors:

                print("   -", error)

        else:

            valid_profiles += 1

    print("\n" + "-" * 70)

    print(f"Valid Profiles   : {valid_profiles}")

    print(f"Invalid Profiles : {invalid_profiles}")

    print("=" * 70)


# ==========================================================
# Top Missions
# ==========================================================

def print_top_missions(profiles, top_n=10):

    print("\n")

    print("=" * 70)
    print(f"TOP {top_n} MISSIONS")
    print("=" * 70)

    sorted_profiles = sorted(

        profiles,

        key=lambda x: x["document_count"],

        reverse=True

    )

    for profile in sorted_profiles[:top_n]:

        print(

            f"{profile['mission']:<22}"

            f" Docs : {profile['document_count']:<3}"

            f" Confidence : {profile['average_confidence']}"

        )

    print("=" * 70)