MISSIONS = [
    "Chandrayaan-1",
    "Chandrayaan-2",
    "Chandrayaan-3",
    "Aditya-L1",
    "Gaganyaan",
    "SpaDeX",
    "NISAR",
    "Mangalyaan"
]


def get_mission(question):

    q = question.lower()

    for mission in MISSIONS:
        if mission.lower() in q:
            return mission

    return question