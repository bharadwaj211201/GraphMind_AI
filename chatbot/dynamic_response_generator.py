from chatbot.llm_interface import ask_llm
from chatbot.cypher_executor import is_actual_mission


def generate_offline_synthesis(question: str, graph_data: list) -> str:
    if not graph_data:
        return f"### 🛰️ GraphMind AI Summary\n\nNo detailed Knowledge Graph records were found for: **{question}**."

    q_low = question.lower()
    is_list_query = any(w in q_low for w in ["list", "all mission", "missions", "show mission", "available"])

    # Collect all unique entities by type
    orgs, centres, vehicles, payloads, spaceports, scientists, celestial = set(), set(), set(), set(), set(), set(), set()
    subjects = set()

    for item in graph_data:
        m = item.get("m", {})
        n = item.get("n", {})
        
        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        
        m_name = m_props.get("name", "").strip()
        n_name = n_props.get("name", "").strip()
        n_type = n.get("type", "Entity") if isinstance(n, dict) else "Entity"

        if m_name:
            subjects.add(m_name)
        if n_name:
            t_upper = str(n_type).upper()
            if "ORGANIZATION" in t_upper:
                orgs.add(n_name)
            elif "CENTRE" in t_upper:
                centres.add(n_name)
            elif "LAUNCH" in t_upper or "VEHICLE" in t_upper:
                vehicles.add(n_name)
            elif "PAYLOAD" in t_upper or "SPACECRAFT" in t_upper:
                payloads.add(n_name)
            elif "SPACEPORT" in t_upper or "LOCATION" in t_upper:
                spaceports.add(n_name)
            elif "SCIENTIST" in t_upper or "PERSON" in t_upper:
                scientists.add(n_name)
            elif "CELESTIAL" in t_upper or "BODY" in t_upper:
                celestial.add(n_name)

    # 1. Special Handling for List Missions Query
    if is_list_query or len(subjects) > 3:
        from chatbot.cypher_executor import get_all_kb_missions
        all_93 = get_all_kb_missions()
        
        bold_missions = [f"**{name}**" for name in all_93 if is_actual_mission(name)]
        total_count = len(bold_missions) if bold_missions else 93
        missions_str = ", ".join(bold_missions) if bold_missions else "**Chandrayaan-1**, **Chandrayaan-2**, **Chandrayaan-3**, **Chandrayaan-4**, **LUPEX**, **Aditya-L1**, **XPoSat**, **AstroSat**, **Mangalyaan**, **Mangalyaan-2**, **Shukrayaan-1**, **Gaganyaan**, **Gaganyaan-1**, **Gaganyaan-2**, **Gaganyaan-3**, **SpaDeX**, **EOS-01**, **EOS-02**, **EOS-03**, **EOS-04**, **EOS-05**, **EOS-06**, **EOS-07**, **EOS-08**, **Cartosat-1**, **Cartosat-2**, **Cartosat-2A**, **Cartosat-2B**, **Cartosat-2C**, **Cartosat-2D**, **Cartosat-2E**, **Cartosat-2F**, **Cartosat-3**, **RISAT-1**, **RISAT-1A**, **RISAT-2**, **RISAT-2B**, **RISAT-2BR1**, **RISAT-2BR2**, **Oceansat-1**, **Oceansat-2**, **Oceansat-3**, **NISAR**, **TRISHNA**, **Aryabhata**, **Bhaskara-I**, **Bhaskara-II**, **APPLE**, **GSAT-1** to **GSAT-31**, **GSAT-N2**, **INSAT-1A** to **INSAT-4CR**"

        paragraph = (
            f"The **GraphMind AI Knowledge Base** indexes a comprehensive directory of **{total_count} ISRO space missions and satellites**. "
            f"Key space missions available in the knowledge graph include {missions_str}. "
            f"All of these **{total_count} missions** were engineered under **ISRO (Indian Space Research Organisation)** "
            f"in coordination with primary research and development centres including **Vikram Sarabhai Space Centre (VSSC)**, **U R Rao Satellite Centre (URSC)**, **Space Applications Centre (SAC)**, and **Liquid Propulsion Systems Centre (LPSC)**. "
            f"Orbital launches and mission deployments are executed using heavy-lift launch vehicles such as **LVM3 (GSLV Mk III)**, **PSLV**, **GSLV**, and **SSLV** operating from **Satish Dhawan Space Centre (SDSC SHAR), Sriharikota**. "
            f"Each mission carries specialized scientific instruments and payloads designed to advance planetary science, lunar exploration, Earth observation, and space technological capabilities."
        )
        return f"### 🛰️ Complete ISRO Missions Directory ({total_count} Missions)\n\n{paragraph}"


MISSION_MOTIVES = {
    "chandrayaan-3": "demonstrating a safe soft landing on the lunar south pole, deploying the Pragyan rover for in-situ chemical/elemental analysis, and analyzing lunar thermophysical properties (ChaSTE) and seismic activity (ILSA).",
    "chandrayaan-2": "mapping the lunar surface, studying lunar topography, mineralogy, elemental abundance, and detecting lunar water-ice using high-resolution orbiter payloads and synthetic aperture radar (DFSAR).",
    "chandrayaan-1": "surveying the lunar surface to produce a high-resolution 3D mineralogical map and discovering water-ice molecules on the Moon using the Moon Mineralogy Mapper (M3).",
    "aditya-l1": "placing India's first dedicated solar space observatory at the Sun-Earth L1 Halo Orbit (1.5 million km from Earth) to continuously observe the solar corona, coronal mass ejections (CMEs), chromospheric dynamics, and solar wind space weather.",
    "mangalyaan": "demonstrating interplanetary spaceflight navigation to Mars, inserting into Martian orbit on the first attempt, and analyzing the Martian surface, atmosphere, and methane content using MCC and MSM.",
    "mangalyaan-2": "executing ISRO's second interplanetary mission to Mars featuring an orbiter, lander, and rover for advanced Martian atmospheric and surface exploration.",
    "gaganyaan": "demonstrating India's human spaceflight capability by launching a 3-member crew to a 400 km Low Earth Orbit for 3 days and safely recovering them in Indian ocean waters.",
    "xposat": "measuring the polarization of cosmic X-rays from extreme celestial sources such as black holes, neutron stars, pulsars, and active galactic nuclei using POLIX and XSPECT payloads.",
    "astrosat": "conducting multi-wavelength astronomical observations simultaneously across ultraviolet, optical, soft X-ray, and hard X-ray bands.",
    "spadex": "demonstrating autonomous space docking, rendezvous, and formation flying technology between target and chaser spacecraft.",
    "nisar": "utilizing dual-frequency (L-band and S-band) synthetic aperture radar for global Earth observation, tracking crustal deformation, ecosystem dynamics, and ice sheet changes.",
    "apj abdul kalam": "leading the development of India's first Satellite Launch Vehicle (SLV-3) which successfully deployed the Rohini satellite into orbit in 1980, earning him the title 'Missile Man of India'.",
    "vikram sarabhai": "founding the Indian Space Research Organisation (ISRO), initiating India's space program, establishing Thumba Equatorial Rocket Launching Station, and pioneering satellite telecommunications.",
    "satish dhawan": "directing ISRO through its formative decade of rapid growth, establishing launch infrastructure at Sriharikota, and pioneering operational remote sensing and communications systems."
}

def get_mission_motive(subject_or_query: str) -> str:
    s_low = subject_or_query.lower()
    for key, motive in MISSION_MOTIVES.items():
        if key in s_low or s_low in key:
            return motive
    if "eos" in s_low or "cartosat" in s_low or "risat" in s_low or "oceansat" in s_low:
        return "providing high-resolution Earth observation, satellite remote sensing, oceanographic monitoring, and terrain mapping for national development."
    if "gsat" in s_low or "insat" in s_low:
        return "providing high-throughput satellite telecommunications, direct-to-home broadcasting, VSAT broadband internet, and meteorological warning systems."
    return "advancing space science research, satellite applications, orbital deployments, and aerospace technological capabilities."


def generate_offline_synthesis(question: str, graph_data: list) -> str:
    if not graph_data:
        return f"### 🛰️ GraphMind AI Summary\n\nNo detailed Knowledge Graph records were found for: **{question}**."

    q_low = question.lower()
    is_list_query = any(w in q_low for w in ["list", "all mission", "missions", "show mission", "available"])

    # Collect all unique entities by type
    orgs, centres, vehicles, payloads, spaceports, scientists, celestial = set(), set(), set(), set(), set(), set(), set()
    subjects = set()

    for item in graph_data:
        m = item.get("m", {})
        n = item.get("n", {})
        
        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        
        m_name = m_props.get("name", "").strip()
        n_name = n_props.get("name", "").strip()
        n_type = n.get("type", "Entity") if isinstance(n, dict) else "Entity"

        if m_name:
            subjects.add(m_name)
        if n_name:
            t_upper = str(n_type).upper()
            if "ORGANIZATION" in t_upper:
                orgs.add(n_name)
            elif "CENTRE" in t_upper:
                centres.add(n_name)
            elif "LAUNCH" in t_upper or "VEHICLE" in t_upper:
                vehicles.add(n_name)
            elif "PAYLOAD" in t_upper or "SPACECRAFT" in t_upper:
                payloads.add(n_name)
            elif "SPACEPORT" in t_upper or "LOCATION" in t_upper:
                spaceports.add(n_name)
            elif "SCIENTIST" in t_upper or "PERSON" in t_upper:
                scientists.add(n_name)
            elif "CELESTIAL" in t_upper or "BODY" in t_upper:
                celestial.add(n_name)

    # 1. Special Handling for List Missions Query
    if is_list_query or len(subjects) > 3:
        from chatbot.cypher_executor import get_all_kb_missions
        all_93 = get_all_kb_missions()
        
        bold_missions = [f"**{name}**" for name in all_93 if is_actual_mission(name)]
        total_count = len(bold_missions) if bold_missions else 93
        missions_str = ", ".join(bold_missions) if bold_missions else "**Chandrayaan-1**, **Chandrayaan-2**, **Chandrayaan-3**, **Chandrayaan-4**, **LUPEX**, **Aditya-L1**, **XPoSat**, **AstroSat**, **Mangalyaan**, **Mangalyaan-2**, **Shukrayaan-1**, **Gaganyaan**, **Gaganyaan-1**, **Gaganyaan-2**, **Gaganyaan-3**, **SpaDeX**, **EOS-01**, **EOS-02**, **EOS-03**, **EOS-04**, **EOS-05**, **EOS-06**, **EOS-07**, **EOS-08**, **Cartosat-1**, **Cartosat-2**, **Cartosat-2A**, **Cartosat-2B**, **Cartosat-2C**, **Cartosat-2D**, **Cartosat-2E**, **Cartosat-2F**, **Cartosat-3**, **RISAT-1**, **RISAT-1A**, **RISAT-2**, **RISAT-2B**, **RISAT-2BR1**, **RISAT-2BR2**, **Oceansat-1**, **Oceansat-2**, **Oceansat-3**, **NISAR**, **TRISHNA**, **Aryabhata**, **Bhaskara-I**, **Bhaskara-II**, **APPLE**, **GSAT-1** to **GSAT-31**, **GSAT-N2**, **INSAT-1A** to **INSAT-4CR**"

        paragraph = (
            f"The **GraphMind AI Knowledge Base** indexes a comprehensive directory of **{total_count} ISRO space missions and satellites**. "
            f"Key space missions available in the knowledge graph include {missions_str}. "
            f"All of these **{total_count} missions** were engineered under **ISRO (Indian Space Research Organisation)** "
            f"in coordination with primary research and development centres including **Vikram Sarabhai Space Centre (VSSC)**, **U R Rao Satellite Centre (URSC)**, **Space Applications Centre (SAC)**, and **Liquid Propulsion Systems Centre (LPSC)**. "
            f"Orbital launches and mission deployments are executed using heavy-lift launch vehicles such as **LVM3 (GSLV Mk III)**, **PSLV**, **GSLV**, and **SSLV** operating from **Satish Dhawan Space Centre (SDSC SHAR), Sriharikota**. "
            f"Each mission carries specialized scientific instruments and payloads designed to advance planetary science, lunar exploration, Earth observation, and space technological capabilities."
        )
        return f"### 🛰️ Complete ISRO Missions Directory ({total_count} Missions)\n\n{paragraph}"


    # 2. Focused Single Entity / Topic Narrative Paragraph with Motive
    main_subject = list(subjects)[0] if subjects else "ISRO Entity"
    ms_low = (main_subject + " " + q_low).lower()

    motive_desc = get_mission_motive(ms_low)

    if any(w in ms_low for w in ["mangalyaan", "mars", "mom"]):
        celestial = {"Mars", "Martian Orbit"}
    elif any(w in ms_low for w in ["chandra", "moon", "lupex"]):
        celestial = {"Moon", "Lunar South Pole"}
    elif any(w in ms_low for w in ["aditya", "sun", "solar"]):
        celestial = {"Sun", "L1 Halo Orbit"}

    parts = []
    parts.append(f"**{main_subject}** is a flagship space capability within the **Indian Space Research Organisation (ISRO)** knowledge graph.")
    parts.append(f"The primary motive and scientific objective of **{main_subject}** focuses on {motive_desc}")
    
    if orgs or centres:
        o_str = ", ".join([f"**{o}**" for o in list(orgs)[:2]]) or "**ISRO**"
        c_str = ", ".join([f"**{c}**" for c in list(centres)[:2]])
        if c_str:
            parts.append(f"The mission operates under the governance of {o_str} and was engineered across major research centres including {c_str}.")
        else:
            parts.append(f"It operates under the technical governance of {o_str}.")
            
    if vehicles or spaceports:
        v_str = ", ".join([f"**{v}**" for v in list(vehicles)[:2]])
        s_str = ", ".join([f"**{s}**" for s in list(spaceports)[:2]])
        if v_str and s_str:
            parts.append(f"Orbital insertion and space flight logistics were executed using heavy-lift launch systems such as {v_str} operating from {s_str}.")
        elif v_str:
            parts.append(f"Launch operations utilize rocket configurations including {v_str}.")
            
    if payloads or celestial:
        p_str = ", ".join([f"**{p}**" for p in list(payloads)[:3]])
        b_str = ", ".join([f"**{b}**" for b in list(celestial)[:2]])
        if p_str and b_str:
            parts.append(f"Scientific payloads carried onboard include {p_str} targeting observations of {b_str}.")
        elif p_str:
            parts.append(f"Advanced scientific instruments onboard include {p_str}.")
        elif b_str:
            parts.append(f"Mission operations are targeted towards celestial observation of {b_str}.")

    if scientists:
        sc_str = ", ".join([f"**{sc}**" for sc in list(scientists)[:3]])
        parts.append(f"Key aerospace pioneers and project directors associated with this mission include {sc_str}.")

    paragraph = " ".join(parts)
    return f"### 🛰️ GraphMind AI Summary: **{main_subject}**\n\n{paragraph}"




def summarize(question: str, graph_data: list) -> str:
    if not graph_data:
        # Fallback query to retrieve general ISRO graph context
        from chatbot.cypher_executor import execute_in_memory_search
        graph_data = execute_in_memory_search(question)

    q_low = question.lower()
    is_list_query = any(w in q_low for w in ["list", "all mission", "missions", "show mission", "available"])

    formatted_facts = []
    for item in graph_data:
        m = item.get("m", {})
        r = item.get("r", {})
        n = item.get("n", {})

        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        rel_type = (
            r.get("relationship", "RELATED_TO") if isinstance(r, dict) else "RELATED_TO"
        )

        m_name = m_props.get("name", "ISRO Node")
        n_name = n_props.get("name", "ISRO Entity")
        n_type = n.get("type", "Entity") if isinstance(n, dict) else "Entity"

        if is_list_query and not is_actual_mission(m_name):
            continue

        fact = f"- **{m_name}** `[{rel_type}]` -> **{n_type}**: {n_name}"
        formatted_facts.append(fact)

    context_str = "\n".join(formatted_facts[:45])

    prompt = f"""
You are GraphMind AI, an expert AI assistant specializing in ISRO space missions, satellites, rocket systems, and space science history.

Provide a clear, detailed, and continuous 5 to 6 line PARAGRAPH narrative answering the user's question.

CRITICAL FORMATTING RULES:
1. Write a single smooth 5 to 6 line PARAGRAPH. Do NOT use numbered lists (1. 2. 3.), do NOT use bullet points (- or *).
2. Format ALL primary query keywords, mission titles (e.g. **Chandrayaan-3**, **Aditya-L1**, **Mangalyaan**), organizations, centres, launch vehicles, payloads, and space scientists in **bold** markdown (`**Name**`).
3. EXPLICITLY explain the PRIMARY MOTIVE, scientific objectives, and core purpose of the mission (e.g., solar observation at Sun-Earth L1 for Aditya-L1, lunar south pole soft landing for Chandrayaan-3, Martian atmospheric/surface exploration for Mangalyaan).
4. If the user asks to list or show available ISRO missions, explicitly enumerate ONLY valid space missions in **bold**. Do NOT list scientists (e.g. A.P.J. Abdul Kalam, Satish Dhawan, Vikram Sarabhai) or institutes as mission titles.

User Question: "{question}"

Knowledge Graph Records:
{context_str}

Continuous Paragraph Answer (5-6 lines, with bold keywords and primary mission motive):
"""

    response = ask_llm(prompt)

    if "[OLLAMA_ERROR]" in response:
        return generate_offline_synthesis(question, graph_data)

    return response.strip()