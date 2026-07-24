import json
import re
from collections import defaultdict

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
        "Axiom Mission-04",
        "Axiom Mission 4"
    ],

    "Aditya-L1": [
        "Aditya-L1",
        "Aditya L1",
        "Solar Mission"
    ],

    "Chandrayaan-1": [
        "Chandrayaan-1",
        "Chandrayaan 1",
        "CH-1"
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

    "Gaganyaan": [
        "Gaganyaan",
        "Human Space Flight",
        "Human Spaceflight"
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

    "INSTRUMENT": "instruments",

    "ASTRONAUT": "astronauts",

    "SCIENTIST": "scientists",

    "COUNTRY": "countries",

    "STATE": "states",

    "CITY": "cities",

    "SPACEPORT": "spaceports",

    "FACILITY": "facilities",

    "LABORATORY": "laboratories",

    "PROGRAM": "programs",

    "TECHNOLOGY": "technologies",

    "CELESTIAL_BODY": "celestial_bodies"
}


# ==========================================================
# Normalize Text
# ==========================================================

def normalize(text):

    if not text:
        return ""

    text = text.lower()

    text = text.replace("-", "")

    text = re.sub(r"\s+", " ", text)

    return text.strip()

# ==========================================================
# Search Text
# ==========================================================

def build_search_text(document):

    return normalize(
        " ".join([
            document.get("title", ""),
            document.get("url", ""),
            document.get("content", "")
        ])
    )

# ==========================================================
# Mission Candidate Generator
# ==========================================================

def get_candidate_missions(document):

    candidates = set()

    entities = document.get("entities", [])

    search_text = build_search_text(document)

    # ==========================================================
    # 1. Extracted Entities
    # ==========================================================

    for entity in entities:

        entity_name = entity.get("name", "")

        entity_type = entity.get("type", "")

        normalized = normalize(entity_name)

        # -------------------------------------------------
        # Direct Mission
        # -------------------------------------------------

        if entity_type == "MISSION":

            candidates.add(entity_name)

            continue

        # ------------------------------------------------
        # Some ISRO missions are classified
        # as SATELLITE in the ontology.
        # 
        # Example:
        # Aditya-L1
        # NISAR
        # Mangalyaan
        # AstroSat
        # EOS
        # -------------------------------------------------

        if entity_type == "SATELLITE":

            for mission, aliases in MISSION_ALIASES.items():

                all_names = aliases + [mission]

                for alias in all_names:

                    if normalize(alias) == normalized:

                        candidates.add(mission)

                        break

    # ================================================
    # 2. Alias Search
    # ================================================

    for mission, aliases in MISSION_ALIASES.items():

        for alias in aliases:

            if normalize(alias) in search_text:

                candidates.add(mission)

                break

    # ================================================
    # 3. Mission Dictionary Search
    # ================================================

    for mission in MISSIONS:

        if normalize(mission) in search_text:

            candidates.add(mission)

    return sorted(candidates)


# ==========================================================
# Mission Detection Engine
# ==========================================================

def detect_primary_mission(document):

    title = normalize(
        document.get("title", "")
    )

    url = normalize(
        document.get("url", "")
    )

    content = normalize(
        document.get("content", "")
    )

    document_type = document.get(
        "document_type",
        "UNKNOWN"
    )

    candidates = get_candidate_missions(document)

    if not candidates:

        return None

    scores = {}

    for mission in candidates:

        score = 0

        reasons = []

        mission_key = normalize(mission)

        # ==========================================
        # Title Match
        # ==========================================

        if mission_key in title:

            score += 120

            reasons.append("TITLE")

        # ==========================================
        # URL Match
        # ==========================================

        if mission_key in url:

            score += 80

            reasons.append("URL")

        # ==========================================
        # Content Frequency
        # ==========================================

        frequency = content.count(mission_key)

        if frequency:

            score += frequency * 3

            reasons.append(
                f"CONTENT({frequency})"
            )

        # =============================================
        # DOCUMENT TYPE BONUS
        # =============================================

        score += DOCUMENT_WEIGHTS.get(
            document_type,
            0
        )

        reasons.append(document_type)

        # ==================================================
        # ENTITY BONUS
        # ==================================================

        entity_bonus = 0

        for entity in document.get("entities", []):

            entity_name = normalize(
                entity.get("name", "")
            )

            entity_type = entity.get("type", "")

            if entity_name != mission_key:
                continue

            if entity_type == "MISSION":

                entity_bonus = 40

            elif entity_type == "SATELLITE":

                entity_bonus = 25
        
        if entity_bonus:

            score += entity_bonus

            reasons.append("ENTITY")

        scores[mission] = {

            "score": score,

            "reason": reasons
        }

    # ==================================================
    # Select Highest Scoring Mission
    # ==================================================

    best_mission, best_data = max(

        scores.items(),

        key = lambda item: item[1]["score"]
    )

    confidence = min(
        round(best_data["score"] / 250, 2),
        1.0
    )

    return {

        "mission": best_mission,

        "confidence": confidence,

        "score": best_data["score"],

        "reason": ", ".join(best_data["reason"])
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

        "instruments": set(),

        "astronauts": set(),

        "scientists": set(),

        "countries": set(),

        "states": set(),

        "cities": set(),

        "spaceports": set(),

        "facilities": set(),

        "laboratories": set(),

        "programs": set(),

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

        # -------------------------------------------------
        # Basic Information
        # -------------------------------------------------

        profile["mission"] = mission

        profile["document_count"] += 1

        profile["documents"].append(
            document.get("title", "")
        )

        profile["urls"].add(
            document.get("url", "")
        )

        profile["sources"].add(
            document.get("source", "Unknown")
        )

        profile["document_types"].add(

            document.get(
                "document_type",
                "UNKNOWN"
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

        for entity in document.get("entities", []):

            entity_name = entity.get("name", "")

            entity_type = entity.get("type", "")

            if entity_type not in ENTITY_MAPPING:
                continue

            profile[
                ENTITY_MAPPING[entity_type]
            ].add(entity_name)

    # ======================================================
    # Final Formatting
    # ======================================================

    mission_profiles = []

    for profile in profiles.values():

    
        # ---------------------------------------------
        # Convert sets into sorted lists
        # ---------------------------------------------

        for key, value in profile.items():

            if isinstance(value, set):

                profile[key] = sorted(value)

        # --------------------------------------------
        # Remove Duplicated Documents
        # --------------------------------------------

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
    # Sort Profiles
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

    print("\n" + "=" * 80)
    print("MISSION PROFILE GENERATION COMPLETED")
    print("=" * 80)

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

    print("-" * 80)

    for profile in profiles:

        print(

            f"{profile['mission']:<22}"

            f" Docs : {profile['document_count']:<3}"

            f" Confidence : {profile['average_confidence']}"

            f" Organizations : {len(profile['organizations']):<3}"

            f" Payloads : {len(profile['payloads']):<3}"

            f" Spacecraft : {len(profile['spacecraft']):<3}"

        )

    print("-" * 80)

    print(f"\nProfiles Saved To : {filepath}")


# ==========================================================
# Knowledge Graph Statistics
# ==========================================================

def print_statistics(profiles):

    print("\n")
    print("=" * 90)
    print("MISSION PROFILE STATISTICS")
    print("=" * 90)

    total_profiles = len(profiles)

    total_documents = sum(

        profile["document_count"]

        for profile in profiles

    )

    print(f"Mission Profiles      : {total_profiles}")
    print(f"Documents Processed   : {total_documents}")

    if total_profiles:

        avg_docs = round(

            total_documents /

            total_profiles,

            2

        )
    else:

        avg_docs = 0

    print(f"Average Docs / Mission   : {avg_docs}")

    # ================================================
    # Count Entites
    # ================================================

    entity_totals = {

        "Organizations": 0,

        "Centers": 0,

        "Launch Vehicles": 0,

        "Rocket Variants": 0,

        "Satellites": 0,

        "Spacecraft": 0,

        "Payloads": 0,

        "Instrument": 0,

        "Scientists": 0,

        "Astronauts": 0,

        "Countries": 0,

        "States": 0,

        "Cities": 0,

        "Spaceports": 0,

        "Facilities": 0,

        "Laboratories": 0,

        "Programs": 0,

        "Technologies": 0,

        "Celestial Bodies": 0

    }

    mapping = {

        "Organizations": "organizations",

        "Centers": "centres",

        "Launch Vehicles": "launch_vehicles",

        "Rocket Variants": "rocket_variants",

        "Satellites": "satellites",

        "Spacecraft": "spacecraft",

        "Payloads": "payloads",

        "Instrument": "instruments",

        "Scientists": "scientists",

        "Astronauts": "astronauts",

        "Countries": "countries",

        "States": "states",

        "Cities": "cities",

        "Spaceports": "spaceports",

        "Facilities": "facilities",

        "Laboratories": "laboratories",

        "Programs": "programs",

        "Technologies": "technologies",

        "Celestial Bodies": "celestial_bodies"
    }

    for profile in profiles:

        for title, key in mapping.items():

            entity_totals[title] += len(

                profile.get(key, [])

            )

    print("\n")
    print("-" * 90)
    print("ENTITY DISTRIBUTION")
    print("-" * 90)

    for entity_type, count in entity_totals.items():

        print(

            f"{entity_type:<22} : {count}"

        )
    
    # ===============================================
    # Confidence
    # ===============================================

    if profiles:

        average_confidence = round(

            sum(

                profile["average_confidence"]

                for profile in profiles

            )

            /

            total_profiles,

            2

        )

        highest = max(

            profile["average_confidence"]

            for profile in profiles

        )

        lowest = min(

            profile["average_confidence"]

            for profile in profiles

        )
    
    else:

        average_confidence = 0

        highest = 0

        lowest = 0

    print("\n")
    print("-" * 90)
    print("CONFIDENCE")
    print("-" * 90)

    print(

        f"Average Confidence  :  {average_confidence}"
    )

    print(

        f"Highest Confidence  :  {highest}"
    )

    print(

        f"Lowest Confidence  :  {lowest}"
    )

    # =======================================
    # Richest Mission
    # =======================================

    richest = None

    richest_score = -1

    for profile in profiles:

        score = 0

        for value in profile.values():

            if isinstance(value, list):

                score += len(value)

        if score > richest_score:

            richest = profile

            richest_score = score
    
    if richest:

        print("\n")
        print("-" * 90)
        print("RICHEST MISSION PROFILE")
        print("-" * 90)

        print(

            f"Mission                : {richest['mission']}"

        )

        print(

            f"Documents            : {richest['document_count']}"

        )

        print(

            f"Knowledge Items        : {richest_score}"

        )

        print(

            f"Average Confidence        : {richest['average_confidence']}"

        )

    print("=" * 90)


# ==========================================================
# Validate Mission Profiles
# ==========================================================

def validate_profiles(profiles):

    print("\n")
    print("=" * 90)
    print("MISSION PROFILE VALIDATION")
    print("=" * 90)

    total_profiles = len(profiles)

    passed = 0

    warnings = []

    for profile in profiles:

        mission = profile["mission"]

        issues = []

        # --------------------------------------------------
        # Mission Name
        # --------------------------------------------------

        if not mission:

            issues.append("Missing mission name")

        # --------------------------------------------------
        # Documents
        # --------------------------------------------------

        if profile["document_count"] == 0:

            issues.append("No supporting documents")

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        if profile["average_confidence"] < 0.60:

            issues.append(
                f"Low confidence ({profile['average_confidence']})"
            )

        # --------------------------------------------------
        # Organizations
        # --------------------------------------------------

        if len(profile["organizations"]) == 0:

            issues.append("No organization linked")

        # --------------------------------------------------
        # URLs
        # --------------------------------------------------

        if len(profile["urls"]) == 0:

            issues.append("No source URL")

        # --------------------------------------------------
        # Document Types
        # --------------------------------------------------

        if len(profile["document_types"]) == 0:

            issues.append("Missing document type")

        # --------------------------------------------------
        # Sources
        # --------------------------------------------------

        if len(profile["sources"]) == 0:

            issues.append("Missing source")

        # --------------------------------------------------
        # Entity Density
        # --------------------------------------------------

        entity_count = (

            len(profile["organizations"])

            + len(profile["centres"])

            + len(profile["launch_vehicles"])

            + len(profile["rocket_variants"])

            + len(profile["satellites"])

            + len(profile["spacecraft"])

            + len(profile["payloads"])

            + len(profile["instruments"])

            + len(profile["scientists"])

            + len(profile["astronauts"])

            + len(profile["countries"])

            + len(profile["states"])

            + len(profile["cities"])

            + len(profile["spaceports"])

            + len(profile["facilities"])

            + len(profile["laboratories"])

            + len(profile["programs"])

            + len(profile["technologies"])

            + len(profile["celestial_bodies"])

        )

        if entity_count < 3:

            issues.append(
                f"Very few linked entities ({entity_count})"
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        if issues:

            warnings.append({

                "mission": mission,

                "issues": issues

            })

        else:

            passed += 1

    # ======================================================
    # Summary
    # ======================================================

    print(f"Profiles Checked : {total_profiles}")

    print(f"Passed           : {passed}")

    print(f"Warnings         : {len(warnings)}")

    # ======================================================
    # Detailed Warnings
    # ======================================================

    if warnings:

        print("\n")

        print("-" * 90)

        print("PROFILE WARNINGS")

        print("-" * 90)

        for warning in warnings:

            print(f"\nMission : {warning['mission']}")

            for issue in warning["issues"]:

                print(f"  • {issue}")

    else:

        print("\nAll mission profiles passed validation.")

    print("=" * 90)

    return warnings


# ==========================================================
# Print Top Mission Profiles
# ==========================================================

def print_top_missions(profiles, top_n=10):

    print("\n")
    print("=" * 100)
    print(f"TOP {min(top_n, len(profiles))} MISSION PROFILES")
    print("=" * 100)

    ranked = sorted(

        profiles,

        key=lambda p: (

            -p["document_count"],

            -p["average_confidence"]

        )

    )

    for i, profile in enumerate(ranked[:top_n], start=1):

        print(f"\n{i}. {profile['mission']}")

        print("-" * 100)

        print(f"Documents          : {profile['document_count']}")

        print(f"Confidence         : {profile['average_confidence']}")

        print(f"Organizations      : {len(profile['organizations'])}")

        print(f"Launch Vehicles    : {len(profile['launch_vehicles'])}")

        print(f"Rocket Variants    : {len(profile['rocket_variants'])}")

        print(f"Satellites         : {len(profile['satellites'])}")

        print(f"Spacecraft         : {len(profile['spacecraft'])}")

        print(f"Payloads           : {len(profile['payloads'])}")

        print(f"Instruments        : {len(profile['instruments'])}")

        print(f"Scientists         : {len(profile['scientists'])}")

        print(f"Astronauts         : {len(profile['astronauts'])}")

        print(f"Countries          : {len(profile['countries'])}")

        print(f"States             : {len(profile['states'])}")

        print(f"Cities             : {len(profile['cities'])}")

        print(f"Spaceports         : {len(profile['spaceports'])}")

        print(f"Facilities         : {len(profile['facilities'])}")

        print(f"Laboratories       : {len(profile['laboratories'])}")

        print(f"Programs           : {len(profile['programs'])}")

        print(f"Technologies       : {len(profile['technologies'])}")

        print(f"Celestial Bodies   : {len(profile['celestial_bodies'])}")

    print("=" * 100)

# ==========================================================
# Main
# ==========================================================

def main():

    INPUT_FILE = "data/raw/isro/structured_missions.json"

    OUTPUT_FILE = "data/raw/mission_profiles.json"

    print("\n")
    print("=" * 100)
    print("MISSION PROFILE BUILDER")
    print("=" * 100)

    documents = load_documents(INPUT_FILE)

    print(f"\nLoaded Documents : {len(documents)}")

    profiles = build_mission_profiles(documents)

    save_profiles(

        profiles,

        OUTPUT_FILE

    )

    print_statistics(

        profiles

    )

    validate_profiles(

        profiles

    )

    print_top_missions(

        profiles,

        top_n=10

    )

    print("\n")

    print("=" * 100)

    print("MISSION PROFILE GENERATION FINISHED")

    print("=" * 100)


if __name__ == "__main__":

    main()