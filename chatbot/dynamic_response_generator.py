from chatbot.llm_interface import ask_llm


def generate_offline_synthesis(question: str, graph_data: list) -> str:

    if not graph_data:
        return f"### 🛰️ GraphMind AI Summary\n\nNo detailed Knowledge Graph records were found for: **{question}**."

    # Group entities by type
    orgs, centres, vehicles, payloads, spaceports, scientists, celestial = set(), set(), set(), set(), set(), set(), set()
    subjects = set()

    for item in graph_data:
        m = item.get("m", {})
        n = item.get("n", {})
        
        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        
        m_name = m_props.get("name", "")
        n_name = n_props.get("name", "")
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

    main_subject = list(subjects)[0] if subjects else "ISRO Entity"

    # Build 5 to 6 line structured narrative answer
    lines = []
    lines.append(f"### 🛰️ GraphMind AI Summary: {main_subject}\n")
    lines.append(f"1. **Core Subject & Scope**: **{main_subject}** is a key subject in ISRO's space knowledge graph, interconnected with core space mission networks.")
    
    if orgs or centres:
        org_str = ", ".join(list(orgs)[:3]) or "ISRO"
        centre_str = ", ".join(list(centres)[:3])
        if centre_str:
            lines.append(f"2. **Organizations & Research Centres**: Directly associated with **{org_str}** and major development centres including **{centre_str}**.")
        else:
            lines.append(f"2. **Organizations**: Operations and governance administered via **{org_str}**.")
    else:
        lines.append("2. **Organizations**: Developed under the auspices of the Indian Space Research Organisation (ISRO).")

    if vehicles or spaceports:
        v_str = ", ".join(list(vehicles)[:3]) or "ISRO Launch Vehicles"
        sp_str = ", ".join(list(spaceports)[:2])
        if sp_str:
            lines.append(f"3. **Launch & Infrastructure**: Integrated with launch capabilities (**{v_str}**) operating from **{sp_str}**.")
        else:
            lines.append(f"3. **Launch Infrastructure**: Utilizes ISRO launch systems such as **{v_str}**.")
    else:
        lines.append("3. **Infrastructure**: Connected to ISRO launch, tracking, and ground control network infrastructure.")

    if payloads or celestial:
        p_str = ", ".join(list(payloads)[:3])
        c_str = ", ".join(list(celestial)[:2])
        if p_str and c_str:
            lines.append(f"4. **Payloads & Target Objectives**: Features instrumentation (**{p_str}**) focused on target domain **{c_str}**.")
        elif p_str:
            lines.append(f"4. **Payloads & Instruments**: Carries scientific equipment including **{p_str}**.")
        else:
            lines.append(f"4. **Target Objectives**: Designed for space observation and planetary study targeting **{c_str}**.")
    else:
        lines.append("4. **Scientific Objectives**: Designed to advance space research, satellite operations, and technology demonstration.")

    if scientists:
        s_str = ", ".join(list(scientists)[:3])
        lines.append(f"5. **Key Pioneers & Scientists**: Historically linked with leading space scientists including **{s_str}**.")
    else:
        lines.append("5. **Operational Leadership**: Executed under the leadership of ISRO space scientists and engineers.")

    lines.append(f"6. **Graph Metadata**: Formatted from {len(graph_data)} verified Knowledge Graph records.")

    return "\n".join(lines)


def summarize(question: str, graph_data: list) -> str:
    if not graph_data:
        # Fallback query to retrieve general ISRO graph context
        from chatbot.cypher_executor import execute_in_memory_search
        graph_data = execute_in_memory_search(question)

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

        fact = f"- **{m_name}** `[{rel_type}]` -> **{n_type}**: {n_name}"
        formatted_facts.append(fact)

    context_str = "\n".join(formatted_facts[:45])

    prompt = f"""
You are GraphMind AI, an expert AI assistant specializing in ISRO space missions, satellites, rocket systems, and space science history.

Provide a clear, detailed, and structured 5 to 6 line summary explaining the core facts, ISRO involvement, technical parameters, launch vehicles, payloads, centres, and scientific outcomes.

Rules:
1. Synthesize a comprehensive 5 to 6 line answer addressing the user's question.
2. Include explicit details from the Knowledge Graph records below (organizations, centres, launch vehicles, payloads, spaceports, and scientists).
3. Format cleanly with bullet points.

User Question: "{question}"

Knowledge Graph Records:
{context_str}

Detailed 5-6 Line Answer:
"""

    response = ask_llm(prompt)

    if "[OLLAMA_ERROR]" in response:
        return generate_offline_synthesis(question, graph_data)

    return response.strip()