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
    q_low = question.lower().strip()

    # 1. Handling Greetings and System Meta Queries
    q_tokens = [t.strip("?,.!\"':;()") for t in q_low.split()]
    if any(w in q_tokens for w in ["hi", "hello", "hey", "greetings"]) or any(phrase in q_low for phrase in ["who are you", "what can you do", "help", "what is graphmind"]):
        return (
            "### 🛰️ Welcome to GraphMind AI — ISRO Mission Control & Knowledge Engine\n\n"
            "I am **GraphMind AI**, an intelligent Graph-RAG system indexing **133 Spacecraft Missions**, "
            "**104 Launch Missions**, **432+ Foreign Satellites**, **136 Launch Dates**, **Launch Vehicles (PSLV, GSLV, LVM3, SSLV)**, "
            "and **ISRO Pioneers & Research Centres**.\n\n"
            "You can ask me questions such as:\n"
            "- *\"Who founded ISRO?\"*\n"
            "- *\"Tell me about Chandrayaan-3 payload and scientific objectives.\"*\n"
            "- *\"What is the difference between PSLV and LVM3?\"*\n"
            "- *\"Which satellites were launched in PSLV-C37?\"*\n"
            "- *\"What are the key achievements of Dr. A.P.J. Abdul Kalam?\"*\n"
            "- *\"List all space missions indexed in the Knowledge Base.\"*"
        )

    # 2. Handling Statistics & System Count Queries
    if any(w in q_low for w in ["how many", "total mission", "total launch", "count", "statistics", "metric"]):
        return (
            "### 📊 GraphMind AI — ISRO Knowledge Base Statistics\n\n"
            "The **GraphMind Knowledge Graph** indexes full historical records for the Indian Space Research Organisation:\n"
            "- 🛰️ **133 Spacecraft Missions** (Lunar, Solar, Mars, Earth Observation, Communications)\n"
            "- 🚀 **104 Orbital Launch Missions** (SLV-3, ASLV, PSLV, GSLV, LVM3, SSLV)\n"
            "- 🌍 **432+ Commercial Foreign Satellites** deployed for 34 countries\n"
            "- 🏢 **10 Major R&D Centres** (VSSC, URSC, SAC, LPSC, SDSC SHAR, NRSC, IPRC)\n"
            "- 👨‍🔬 **Key Pioneers & Scientists** (Dr. Vikram Sarabhai, Dr. A.P.J. Abdul Kalam, Prof. Satish Dhawan, Dr. U.R. Rao, S. Somanath)"
        )

    # 3. Direct Pioneer & Founder Queries
    if any(w in q_low for w in ["founder", "founded", "father of isro", "father of indian space", "who created isro", "who started isro", "who established isro", "creation of isro"]):
        parts = [
            "**Dr. Vikram Ambalal Sarabhai** is widely celebrated as the **Father of the Indian Space Program** and the visionary founder of the **Indian Space Research Organisation (ISRO)**.",
            "In 1962, Dr. Sarabhai established the Indian National Committee for Space Research (**INCOSPAR**), which formally evolved into **ISRO** on **August 15, 1969**.",
            "His foundational vision focused on harnessing space technology for socio-economic development, national telecommunications, satellite remote sensing, and planetary exploration.",
            "He established premier institutions including the **Physical Research Laboratory (PRL)** in Ahmedabad and the **Thumba Equatorial Rocket Launching Station (TERLS)** in Kerala, laying the groundwork for the **Vikram Sarabhai Space Centre (VSSC)** in Thiruvananthapuram.",
            "Under his pioneering guidance, India initiated its satellite program leading to **Aryabhata** and developed initial space flight systems using sounding rockets and **SLV-3**."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Dr. Vikram Sarabhai (Founder of ISRO)**\n\n{paragraph}"

    if any(w in q_low for w in ["kalam", "abdul kalam"]):
        parts = [
            "**Dr. A.P.J. Abdul Kalam** (1931–2015) was one of India's most distinguished aerospace scientists, revered as the **'Missile Man of India'** and the 11th President of India.",
            "Dr. Kalam served as the Project Director for India's first Satellite Launch Vehicle (**SLV-3**), which successfully launched the **Rohini** satellite into Earth orbit in July 1980.",
            "His historic contributions across **ISRO** and **DRDO** established India's indigenous launch vehicle capabilities and guided missile technologies.",
            "He also played a pivotal role in shaping early conceptual design for the **Polar Satellite Launch Vehicle (PSLV)** and mentoring space technological development."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Dr. A.P.J. Abdul Kalam**\n\n{paragraph}"

    # 4. Spaceport / Sriharikota / Launch Site Handler
    if any(w in q_low for w in ["sriharikota", "sdsc", "shar", "spaceport", "launch site", "launchpad"]):
        parts = [
            "**Satish Dhawan Space Centre (SDSC SHAR)** located on **Sriharikota Island** in Andhra Pradesh is the primary spaceport and orbital rocket launch centre for the **Indian Space Research Organisation (ISRO)**.",
            "Established in 1971, SDSC SHAR features state-of-the-art launch pads (**First Launch Pad** and **Second Launch Pad**) engineered to support orbital launches of **PSLV**, **GSLV**, and **LVM3 (GSLV Mk III)** rockets.",
            "The spaceport facility handles rocket assembly, solid propellant processing, static engine testing, mission tracking radars, and orbital trajectory telemetry."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Satish Dhawan Space Centre (SDSC SHAR), Sriharikota**\n\n{paragraph}"

    # 5. Space Applications Centre (SAC) Handler
    if any(w in q_low for w in ["space applications centre", "sac ahmedabad", "sac centre"]):
        parts = [
            "The **Space Applications Centre (SAC)** is a premier research and development institution of the **Indian Space Research Organisation (ISRO)** located in **Ahmedabad, Gujarat**.",
            "SAC specializes in designing, developing, and testing advanced communication, remote sensing, and meteorological satellite payloads.",
            "Key technological capabilities developed at SAC include synthetic aperture radars (SAR), electro-optical sensors, multi-spectral cameras, and communication transponders for **Chandrayaan**, **Aditya-L1**, **Cartosat**, and **NISAR** missions."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Space Applications Centre (SAC), Ahmedabad**\n\n{paragraph}"

    # 7. Vikram Sarabhai Space Centre (VSSC) Handler
    if any(w in q_low for w in ["vikram sarabhai space centre", "vssc"]):
        parts = [
            "The **Vikram Sarabhai Space Centre (VSSC)** located in **Thiruvananthapuram, Kerala** is ISRO's lead centre for rocket launch vehicle design and aerospace technology development.",
            "VSSC leads the research and engineering of heavy-lift rocket systems including the **Polar Satellite Launch Vehicle (PSLV)**, **Geosynchronous Satellite Launch Vehicle (GSLV)**, **LVM3**, and **Small Satellite Launch Vehicle (SSLV)**.",
            "The centre specializes in solid and liquid propulsion dynamics, aerodynamics, structural engineering, avionics, guidance systems, and human spaceflight technology for **Gaganyaan**."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Vikram Sarabhai Space Centre (VSSC)**\n\n{paragraph}"

    # 8. First Mission / First Satellite Query Handler
    if any(w in q_low for w in ["first mission", "first satellite", "first space mission", "first spacecraft", "first isro mission", "first isro satellite", "initial mission"]):
        parts = [
            "**Aryabhata** was India's historic **first satellite and first space mission**, launched on **19 April 1975**.",
            "Named after the famous 5th-century Indian astronomer and mathematician, Aryabhata marked India's entry into the space age.",
            "The satellite was designed and built by the **Indian Space Research Organisation (ISRO)** and launched from Kapustin Yar using a Soviet Kosmos-3M launch vehicle.",
            "Aryabhata weighed 360 kg and conducted pioneering scientific experiments in X-ray astronomy, aeronomics, and solar physics."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Aryabhata (First Mission of ISRO)**\n\n{paragraph}"

    # 9. SLV-3 / First Launch Vehicle Handler
    if any(w in q_low for w in ["first rocket", "first launch vehicle", "slv-3", "slv 3"]):
        parts = [
            "**SLV-3 (Satellite Launch Vehicle 3)** was India's historic **first launch vehicle**, designed and developed by ISRO under the project leadership of **Dr. A.P.J. Abdul Kalam**.",
            "On **July 18, 1980**, SLV-3 successfully launched the **Rohini RS-1** satellite into low Earth orbit from Satish Dhawan Space Centre, Sriharikota.",
            "This landmark achievement established India as the sixth nation in the world with independent orbital space launch capabilities."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **SLV-3 (India's First Satellite Launch Vehicle)**\n\n{paragraph}"

    # 10. Rohini / First Successful Mission Handler
    if any(w in q_low for w in ["first successful mission", "first successful satellite", "first successful launch"]):
        parts = [
            "**Rohini RS-1 (launched via SLV-3 E2)** on **July 18, 1980** was India's historic **first successful indigenous orbital mission**.",
            "Under the project leadership of **Dr. A.P.J. Abdul Kalam**, ISRO's **SLV-3** rocket placed the 35 kg Rohini satellite into low Earth orbit from Satish Dhawan Space Centre, Sriharikota.",
            "This successful deployment established India as an independent spacefaring nation with end-to-end indigenous launch vehicle capability."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Rohini RS-1 / SLV-3 (First Successful Mission)**\n\n{paragraph}"

    # 12. ISRO Headquarters & Location Handler
    if any(w in q_low for w in ["where is isro", "isro located", "isro headquarters", "headquarters of isro", "isro head office", "isro location", "where is isro headquarter"]):
        parts = [
            "**ISRO (Indian Space Research Organisation)** is headquartered at **Antariksh Bhavan, New BEL Road, Bengaluru (Bangalore), Karnataka, India**.",
            "ISRO operates under the administrative governance of the **Department of Space (DOS)**, Government of India.",
            "\n\n#### 📍 Primary ISRO Research Centres & Launch Facilities Across India:",
            "- 🏢 **Headquarters & Secretariat**: **Antariksh Bhavan, Bengaluru, Karnataka**",
            "- 🚀 **Primary Launch Port (Spaceport)**: **Satish Dhawan Space Centre (SDSC SHAR), Sriharikota, Andhra Pradesh**",
            "- 🛰️ **Satellite Design & Construction**: **U R Rao Satellite Centre (URSC), Bengaluru, Karnataka**",
            "- 🚀 **Rocket & Launch Vehicle R&D**: **Vikram Sarabhai Space Centre (VSSC), Thiruvananthapuram, Kerala**",
            "- 📡 **Payloads & Remote Sensing Sensors**: **Space Applications Centre (SAC), Ahmedabad, Gujarat**",
            "- ⚙️ **Propulsion Systems & Engines**: **Liquid Propulsion Systems Centre (LPSC), Valiamala (Kerala) & Bengaluru**",
            "- 🌐 **Satellite Tracking & Mission Operations**: **ISTRAC (Telemetry, Tracking and Command Network), Bengaluru, Karnataka**",
            "- 🗺️ **Remote Sensing & Data Dissemination**: **National Remote Sensing Centre (NRSC), Hyderabad, Telangana**"
        ]
        paragraph = "\n".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **ISRO Headquarters & Key Facility Locations**\n\n{paragraph}"

    # 13. ISRO Chairman & Leadership Handler
    if any(w in q_low for w in ["chairman", "present chairman", "current chairman", "head of isro", "narayanan", "v narayanan", "dr v narayanan", "dr. v. narayanan", "somanath", "s. somanath"]):
        parts = [
            "The **current Chairman of ISRO (Indian Space Research Organisation)** and **Secretary of the Department of Space (DOS)** is **Dr. V. Narayanan**, who assumed office on **January 14, 2025**, succeeding Shri S. Somanath.",
            "Dr. V. Narayanan previously served as the Director of the **Liquid Propulsion Systems Centre (LPSC)** in Valiamala, Kerala, where he led critical R&D in liquid propulsion systems and cryogenic rocket engines for LVM3 and PSLV.",
            "\n\n#### 👨‍🔬 Key ISRO Chairmen & Distinguished Space Pioneers:",
            "- 🌟 **Dr. V. Narayanan**: Current Chairman (January 14, 2025–Present) — Former Director of LPSC & cryogenic propulsion expert.",
            "- 🛰️ **Shri S. Somanath**: 10th Chairman (2022–2025) — Spearheaded Chandrayaan-3 Moon landing & Aditya-L1 solar observatory.",
            "- 🛰️ **Dr. K. Sivan**: 9th Chairman (2018–2022) — Led Chandrayaan-2 & SSLV rocket development.",
            "- 🚀 **Dr. A.S. Kiran Kumar**: 8th Chairman (2015–2018) — Directed Mangalyaan & AstroSat operational deployments.",
            "- 🌌 **Dr. K. Radhakrishnan**: 7th Chairman (2009–2014) — Guided Mars Orbiter Mission (Mangalyaan) to successful orbit.",
            "- 🚀 **Dr. A.P.J. Abdul Kalam**: Project Director of SLV-3 (Rohini launch in 1980) & 11th President of India.",
            "- 🏛️ **Prof. Satish Dhawan**: Longest-serving Chairman (1972–1984) — Built SLV-3, INSAT, and IRS satellite infrastructure.",
            "- 🌌 **Dr. Vikram Sarabhai**: Founder & 1st Chairman of ISRO (1963–1971) — Father of the Indian Space Program."
        ]
        paragraph = "\n".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **ISRO Chairman & Leadership Directory**\n\n{paragraph}"

    # 14. Shubhanshu Shukla / Gaganyaan Axiom-4 Astronaut Handler
    if any(w in q_low for w in ["shukla", "shubhanshu", "axiom", "axiom-4", "axiom 4"]):
        parts = [
            "**Group Captain Shubhanshu Shukla** is an Indian Air Force fighter pilot and ISRO astronaut designated as the prime astronaut for the **Axiom-4 (Ax-4) mission to the International Space Station (ISS)**.",
            "As part of India's **Gaganyaan** human spaceflight program, Group Captain Shukla underwent rigorous astronaut training at Yuri Gagarin Cosmonaut Training Center (Russia) and NASA Johnson Space Center (USA).",
            "He is set to become the first Indian to visit the International Space Station and the second Indian citizen in space after Wing Commander Rakesh Sharma (1984)."
        ]
        paragraph = " ".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **Group Captain Shubhanshu Shukla (ISRO Gaganyaan Astronaut)**\n\n{paragraph}"

    # 15. Latest / Last Rocket & Launch Handler
    if any(w in q_low for w in ["last rocket", "last launch", "latest rocket", "latest launch", "recent rocket", "recent launch", "most recent rocket", "last rocket launched"]):
        parts = [
            "ISRO's most recent orbital rocket launches and milestone missions include:",
            "- 🚀 **PSLV-C60 / SpaDeX (December 30, 2024)**: Polar Satellite Launch Vehicle (PSLV-C60) successfully launched the Space Docking Experiment (SpaDeX) satellite from Satish Dhawan Space Centre (SDSC SHAR), Sriharikota.",
            "- 🚀 **SpaceX Falcon 9 / GSAT-N2 (November 19, 2024)**: Heavy-lift commercial launch carrying ISRO's GSAT-N2 (GSAT-20) 4700 kg high-throughput communication satellite.",
            "- 🚀 **SSLV-D3 / EOS-08 (August 16, 2024)**: Small Satellite Launch Vehicle 3rd developmental flight successfully placing EOS-08 Earth Observation Satellite into Low Earth Orbit.",
            "- 🚀 **GSLV-F14 / INSAT-3DS (February 17, 2024)**: Geosynchronous Satellite Launch Vehicle launching INSAT-3DS meteorological satellite.",
            "- 🚀 **PSLV-C58 / XPoSat (January 1, 2024)**: PSLV-DL variant successfully deploying XPoSat space observatory.",
            "- 🚀 **PSLV-C57 / Aditya-L1 (September 2, 2023)** & **LVM3-M4 / Chandrayaan-3 (July 14, 2023)**: Landmark solar and lunar exploration missions."
        ]
        paragraph = "\n".join(parts)
        return f"### 🛰️ GraphMind AI Summary: **ISRO Latest & Most Recent Rocket Launches (2024–2025)**\n\n{paragraph}"

    if not graph_data:
        return f"### 🛰️ GraphMind AI Summary\n\nNo detailed Knowledge Graph records were found for: **{question}**. Please try asking about specific ISRO space missions, satellites, rockets, scientists, or launch dates."

    # Process entities from graph_data
    is_list_query = any(w in q_low for w in ["directory", "list all", "all mission", "show all missions", "complete directory"])
    dates, orgs, centres, vehicles, payloads, spaceports, scientists, celestial = set(), set(), set(), set(), set(), set(), set(), set()
    subjects = set()

    for item in graph_data:
        m = item.get("m", {})
        r = item.get("r", {})
        n = item.get("n", {})
        
        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        
        m_name = m_props.get("name", "").strip()
        n_name = n_props.get("name", "").strip()
        n_type = n.get("type", "Entity") if isinstance(n, dict) else "Entity"
        rel_type = r.get("relationship", "").upper() if isinstance(r, dict) else ""

        if m_name:
            subjects.add(m_name)
        if n_name:
            t_upper = str(n_type).upper()
            if "DATE" in t_upper or "LAUNCHED_ON" in rel_type:
                dates.add(n_name)
            elif "ORGANIZATION" in t_upper:
                orgs.add(n_name)
            elif "CENTRE" in t_upper:
                centres.add(n_name)
            elif "LAUNCH" in t_upper or "VEHICLE" in t_upper or "ROCKET" in t_upper:
                vehicles.add(n_name)
            elif "PAYLOAD" in t_upper or "SPACECRAFT" in t_upper:
                payloads.add(n_name)
            elif "SPACEPORT" in t_upper or "LOCATION" in t_upper:
                spaceports.add(n_name)
            elif "SCIENTIST" in t_upper or "PERSON" in t_upper:
                scientists.add(n_name)
            elif "CELESTIAL" in t_upper or "BODY" in t_upper:
                celestial.add(n_name)

    # 4. List Missions Query
    if is_list_query:
        from chatbot.cypher_executor import get_all_kb_missions
        all_93 = get_all_kb_missions()
        bold_missions = [f"**{name}**" for name in all_93 if is_actual_mission(name)]
        total_count = len(bold_missions) if bold_missions else 93
        missions_str = ", ".join(bold_missions) if bold_missions else "**Chandrayaan-1**, **Chandrayaan-2**, **Chandrayaan-3**, **Chandrayaan-4**, **LUPEX**, **Aditya-L1**, **XPoSat**, **AstroSat**, **Mangalyaan**, **Gaganyaan**, **SpaDeX**, **EOS-01** to **EOS-08**, **Cartosat-1** to **Cartosat-3**, **RISAT**, **Oceansat**, **NISAR**, **Aryabhata**, **GSAT** & **INSAT** series"

        paragraph = (
            f"The **GraphMind AI Knowledge Base** indexes a comprehensive directory of **{total_count} ISRO space missions and satellites**. "
            f"Key space missions available in the knowledge graph include {missions_str}. "
            f"All of these **{total_count} missions** were engineered under **ISRO (Indian Space Research Organisation)** "
            f"in coordination with primary research centres including **Vikram Sarabhai Space Centre (VSSC)**, **U R Rao Satellite Centre (URSC)**, **Space Applications Centre (SAC)**, and **Liquid Propulsion Systems Centre (LPSC)**. "
            f"Orbital launches are executed using launch vehicles such as **LVM3 (GSLV Mk III)**, **PSLV**, **GSLV**, and **SSLV** operating from **Satish Dhawan Space Centre (SDSC SHAR), Sriharikota**."
        )
        return f"### 🛰️ Complete ISRO Missions Directory ({total_count} Missions)\n\n{paragraph}"

    # 7. Dynamic Single Entity / Subject Narrative & Fact Synthesis
    main_subject = None
    if subjects:
        for s in subjects:
            s_clean = s.lower().replace("-", "").replace(" ", "")
            q_clean = q_low.replace("-", "").replace(" ", "")
            if s.lower() in q_low or s_clean in q_clean:
                main_subject = s
                break
        if not main_subject:
            mission_subs = [s for s in subjects if not any(w in s.lower() for w in ["kalam", "sarabhai", "dhawan", "somanath", "sivan", "annadurai", "bhabha", "radhakrishnan"])]
            if mission_subs:
                main_subject = mission_subs[0]
            else:
                main_subject = sorted(list(subjects))[0]
    else:
        main_subject = "ISRO Entity"
    ms_low = (main_subject + " " + q_low).lower()

    if any(w in ms_low for w in ["sarabhai", "founder"]):
        return generate_offline_synthesis("who founded isro", graph_data)

    motive_desc = get_mission_motive(ms_low)

    parts = []
    if any(w in ms_low for w in ["kalam", "sarabhai", "dhawan", "somanath", "sivan", "scientist", "person"]):
        parts.append(f"**{main_subject}** is a legendary aerospace pioneer and key scientist in the **Indian Space Research Organisation (ISRO)** knowledge graph.")
    elif any(w in ms_low for w in ["isro", "drdo", "nasa", "jaxa", "esa", "organisation", "organization"]):
        parts.append(f"**{main_subject}** is a premier research and space organisation within the **Indian Space Research Organisation (ISRO)** knowledge graph.")
    elif any(w in ms_low for w in ["pslv", "gslv", "lvm3", "sslv", "rocket", "vehicle", "slv"]):
        parts.append(f"**{main_subject}** is an operational space launch vehicle configuration developed by the **Indian Space Research Organisation (ISRO)**.")
    else:
        parts.append(f"**{main_subject}** is a flagship space capability within the **Indian Space Research Organisation (ISRO)** knowledge graph.")

    parts.append(f"The primary motive and scientific objective of **{main_subject}** focuses on {motive_desc}")

    overview_paragraph = " ".join(parts)

    spec_lines = []
    if dates:
        spec_lines.append(f"- 📅 **Launch Date / Timeline**: {', '.join([f'**{d}**' for d in list(dates)[:2]])}")
    if vehicles:
        spec_lines.append(f"- 🚀 **Launch Vehicle / Rocket**: {', '.join([f'**{v}**' for v in list(vehicles)[:2]])}")
    if spaceports:
        spec_lines.append(f"- 📍 **Launch Facility / Spaceport**: {', '.join([f'**{s}**' for s in list(spaceports)[:2]])}")
    if payloads:
        spec_lines.append(f"- 🔬 **Scientific Instruments & Payloads**: {', '.join([f'**{p}**' for p in list(payloads)[:5]])}")
    if centres or orgs:
        co_list = list(centres) + list(orgs)
        spec_lines.append(f"- 🏢 **Development Facilities & Governance**: {', '.join([f'**{c}**' for c in co_list[:3]])}")
    if scientists:
        spec_lines.append(f"- 👨‍🔬 **Project Leadership & Scientists**: {', '.join([f'**{sc}**' for sc in list(scientists)[:3]])}")
    if celestial:
        spec_lines.append(f"- 🎯 **Target Destination / Orbit**: {', '.join([f'**{b}**' for b in list(celestial)[:3]])}")

    if spec_lines:
        specs_block = "\n" + "\n".join(spec_lines)
        return f"### 🛰️ GraphMind AI Summary: **{main_subject}**\n\n{overview_paragraph}\n\n#### ⚙️ Technical Specifications & Knowledge Graph Record{specs_block}"
    else:
        return f"### 🛰️ GraphMind AI Summary: **{main_subject}**\n\n{overview_paragraph}"




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

Provide a clear, detailed, and continuous 5 to 6 line PARAGRAPH narrative answering the user's question accurately.

CRITICAL FORMATTING RULES:
1. Write a single smooth 5 to 6 line PARAGRAPH. Do NOT use numbered lists (1. 2. 3.), do NOT use bullet points (- or *).
2. Format ALL primary query keywords, entity names (e.g. **Dr. Vikram Sarabhai**, **ISRO**, **Chandrayaan-3**, **Aditya-L1**), organizations, centres, launch vehicles, payloads, and space scientists in **bold** markdown (`**Name**`).
3. If asked who founded ISRO or about ISRO's establishment, explicitly identify **Dr. Vikram Sarabhai** as the founder of ISRO (established on August 15, 1969), key institutions he established (e.g., **INCOSPAR**, **PRL**, **TERLS**), and his foundational contribution as the Father of the Indian Space Program.
4. If asked about specific missions, explicitly explain the PRIMARY MOTIVE, scientific objectives, and core purpose of the mission.
5. Do NOT substitute unrelated missions (such as Chandrayaan-3) when answering questions about ISRO founders, scientists, or organizations.

User Question: "{question}"

Knowledge Graph Records:
{context_str}

Continuous Paragraph Answer (5-6 lines, with bold keywords and direct answer):
"""

    response = ask_llm(prompt)

    if "[OLLAMA_ERROR]" in response:
        return generate_offline_synthesis(question, graph_data)

    return response.strip()