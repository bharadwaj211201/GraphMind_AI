from chatbot.llm_interface import ask_llm


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
        return "### ISRO Knowledge Graph Facts\n\n" + context_str

    return response.strip()