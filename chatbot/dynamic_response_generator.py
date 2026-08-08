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
        all_missions = [f"**{name}**" for name in subjects if is_actual_mission(name)]
        if not all_missions:
            all_missions = [
                "**Chandrayaan-3**", "**Aditya-L1**", "**Gaganyaan**", "**Mangalyaan**",
                "**AstroSat**", "**XPoSat**", "**SpaDeX**", "**Cartosat-3**", "**EOS-06**"
            ]
        missions_str = ", ".join(all_missions[:10])

        org_name = list(orgs)[0] if orgs else "ISRO (Indian Space Research Organisation)"
        clean_org = str(org_name).replace("*", "").strip()
        if not clean_org or any(p in clean_org.lower() for p in ["physical research laboratory", "prl", "kalam", "sarabhai", "dhawan"]):
            clean_org = "ISRO (Indian Space Research Organisation)"
        org_str = f"**{clean_org}**"




        centre_str = ", ".join([f"**{c}**" for c in list(centres)[:3]]) or "**Vikram Sarabhai Space Centre (VSSC)** and **U R Rao Satellite Centre (URSC)**"
        vehicle_str = ", ".join([f"**{v}**" for v in list(vehicles)[:3]]) or "**LVM3 (GSLV Mk III)** and **PSLV**"
        
        paragraph = (
            f"The **GraphMind AI Knowledge Base** indexes a comprehensive directory of **ISRO space missions** "
            f"spanning lunar exploration, solar observation, human spaceflight, satellite communications, and deep space research. "
            f"Key space missions available in the knowledge graph include {missions_str}. "
            f"All of these missions were developed under the **{org_str}** in coordination with primary research and development centres including {centre_str}. "
            f"Orbital launches and mission deployments are executed using heavy-lift and reliable launch vehicles such as {vehicle_str} operating from **Satish Dhawan Space Centre (SDSC SHAR), Sriharikota**. "
            f"Each mission carries specialized scientific instruments and payloads designed to advance planetary science, Earth observation, and space technological capabilities."
        )
        return f"### 🛰️ ISRO Missions Catalog\n\n{paragraph}"

    # 2. Focused Single Entity / Topic Narrative Paragraph
    main_subject = list(subjects)[0] if subjects else "ISRO Entity"
    
    parts = []
    parts.append(f"**{main_subject}** is a prominent space entity within the **Indian Space Research Organisation (ISRO)** knowledge graph.")
    
    if orgs or centres:
        o_str = ", ".join([f"**{o}**" for o in list(orgs)[:2]]) or "**ISRO**"
        c_str = ", ".join([f"**{c}**" for c in list(centres)[:2]])
        if c_str:
            parts.append(f"It operates under the governance of {o_str} and is engineered across major technical centres including {c_str}.")
        else:
            parts.append(f"It operates under the governance and technical direction of {o_str}.")
            
    if vehicles or spaceports:
        v_str = ", ".join([f"**{v}**" for v in list(vehicles)[:2]])
        s_str = ", ".join([f"**{s}**" for s in list(spaceports)[:2]])
        if v_str and s_str:
            parts.append(f"Orbital insertion and space flight logistics utilize launch systems such as {v_str} operating from spaceports like {s_str}.")
        elif v_str:
            parts.append(f"Launch operations utilize specialized rocket configurations including {v_str}.")
            
    if payloads or celestial:
        p_str = ", ".join([f"**{p}**" for p in list(payloads)[:3]])
        b_str = ", ".join([f"**{b}**" for b in list(celestial)[:2]])
        if p_str and b_str:
            parts.append(f"The mission setup incorporates scientific instruments including {p_str} targeting observation of {b_str}.")
        elif p_str:
            parts.append(f"Scientific objectives are carried out via advanced payloads such as {p_str}.")
        elif b_str:
            parts.append(f"Mission operations are targeted towards celestial observation of {b_str}.")

    if scientists:
        sc_str = ", ".join([f"**{sc}**" for sc in list(scientists)[:3]])
        parts.append(f"Key aerospace pioneers and scientists associated with this work include {sc_str}.")

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
2. Format ALL primary query keywords, mission titles (e.g. **Chandrayaan-3**, **Aditya-L1**), organizations, centres, launch vehicles, payloads, and space scientists in **bold** markdown (`**Name**`).
3. If the user asks to list or show available ISRO missions, explicitly enumerate ONLY valid space missions in **bold**. Do NOT list scientists (e.g. A.P.J. Abdul Kalam, Satish Dhawan, Vikram Sarabhai) or institutes as mission titles.

User Question: "{question}"

Knowledge Graph Records:
{context_str}

Continuous Paragraph Answer (5-6 lines, with bold keywords):
"""

    response = ask_llm(prompt)

    if "[OLLAMA_ERROR]" in response:
        return generate_offline_synthesis(question, graph_data)

    return response.strip()