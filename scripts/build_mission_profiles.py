"""
Mission Profile Builder Pipeline
--------------------------------
Loads processed documents, builds mission profiles,
validates them, prints statistics and saves the output.
"""

import os
import sys
import time

# ----------------------------------------------------------
# Add Project Root to Python Path
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ----------------------------------------------------------
# Import Mission Builder
# ----------------------------------------------------------

from processors.mission_builder import (
    load_documents,
    build_mission_profiles,
    save_profiles,
    print_statistics,
    validate_profiles,
    print_top_missions
)

# ----------------------------------------------------------
# File Paths
# ----------------------------------------------------------

INPUT_FILE = "data/raw/raw_documents.json"

OUTPUT_FILE = (
    "data/processed/mission_profiles/"
    "mission_profiles.json"
)

# ----------------------------------------------------------
# Main Pipeline
# ----------------------------------------------------------

def main():

    print("\n" + "=" * 70)
    print("MISSION PROFILE PIPELINE")
    print("=" * 70)

    start_time = time.time()

    # ------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print(f"\nERROR : Input file not found")

        print(INPUT_FILE)

        return

    # ------------------------------------------------------

    documents = load_documents(INPUT_FILE)

    print(f"\nDocuments Loaded : {len(documents)}")

    # ------------------------------------------------------

    mission_profiles = build_mission_profiles(
        documents
    )

    print(
        f"Mission Profiles Built : "
        f"{len(mission_profiles)}"
    )

    # ------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    save_profiles(
        mission_profiles,
        OUTPUT_FILE
    )

    # ------------------------------------------------------

    print_statistics(
        mission_profiles
    )

    validate_profiles(
        mission_profiles
    )

    print_top_missions(
        mission_profiles,
        top_n=10
    )

    # ------------------------------------------------------

    execution_time = round(
        time.time() - start_time,
        2
    )

    print("\n" + "=" * 70)
    print("PIPELINE FINISHED")
    print("=" * 70)

    print(f"Execution Time : {execution_time} sec")

    print(f"Output File    : {OUTPUT_FILE}")

    print("=" * 70)


# ----------------------------------------------------------
# Entry Point
# ----------------------------------------------------------

if __name__ == "__main__":

    main()  