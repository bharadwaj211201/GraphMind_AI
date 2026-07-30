from chatbot.llm_interface import ask_llm


def summarize(question: str, graph_data: list) -> str:
    if not graph_data:
        return "No relevant information was found in the Knowledge Graph for your query."

    formatted_facts = []
    for item in graph_data:
        m = item.get("m", {})
        r = item.get("r", {})
        n = item.get("n", {})

        m_props = m.get("properties", {}) if isinstance(m, dict) else {}
        n_props = n.get("properties", {}) if isinstance(n, dict) else {}
        rel_type = (
            r.get("relationship", "RELATED_TO") if isinstance(r, dict) else ""
        )

        m_name = m_props.get("name", "Unknown Node")
        n_name = n_props.get("name", "Unknown Entity")
        n_type = n.get("type", "Entity") if isinstance(n, dict) else "Entity"

        fact = f"- [{m_name}] --({rel_type})--> [{n_type}: {n_name}]"
        formatted_facts.append(fact)

    context_str = "\n".join(formatted_facts[:40])

    prompt = f"""
You are GraphMind AI, an intelligent assistant for ISRO space missions.
Answer the user's question accurately using ONLY the Knowledge Graph records below.

Rules:
1. Extract all relevant details (dates, launch vehicles, testing facilities, organizations, ISRO involvement).
2. Note that ISRO (Indian Space Research Organisation) operates these missions and test facilities like ISRO Propulsion Complex.
3. If specific exact dates (like launch dates vs engine test dates) are listed in the records, explain what the date represents based on the mission context.
4. Keep the answer clear, professional, and well-structured using bullet points where appropriate.

User Question: "{question}"

Knowledge Graph Records:
{context_str}

Detailed Answer:
"""

    response = ask_llm(prompt)
    return response.strip()