from chatbot.llm_interface import ask_llm


def summarize(question, graph_data):

    if not graph_data:
        return "No information found in the Knowledge Graph."

    prompt = f"""
You are GraphMind AI.

You are answering ONLY from Neo4j results.

Knowledge Graph Result

{graph_data}

User Question

{question}

Rules

1. NEVER invent facts.

2. NEVER use outside knowledge.

3. ONLY use information shown above.

4. If something is missing, simply ignore it.

5. Write a natural paragraph.

6. Do not print Python lists.

7. Do not introduce yourself.

8. Do not ask another question.

Answer:
"""

    return ask_llm(prompt)