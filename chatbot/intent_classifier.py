import os
import ollama

# Bypass system HTTP proxies for local Ollama requests
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

MODEL = "llama3.2:3b"


def get_intent(question: str) -> str:
    if not question:
        return "unknown"

    q_lower = question.lower().strip()

    # Rule-based fast intent matching
    if any(k in q_lower for k in ["list mission", "all mission", "show mission", "list all mission"]):
        return "list_missions"
    if any(k in q_lower for k in ["list organization", "all organization", "show organization", "list org"]):
        return "list_organizations"
    if any(k in q_lower for k in ["list people", "show scientist", "list scientist", "who are the scientists"]):
        return "list_people"
    if any(k in q_lower for k in ["list location", "show location"]):
        return "list_locations"
    if any(k in q_lower for k in ["list date", "show date"]):
        return "list_dates"

    prompt = f"""
You are an AI Intent Classifier.

Your job is to classify user questions into ONE of these intents.

Return ONLY ONE WORD.

Possible intents:
mission
organization
person
location
date
comparison
list_missions
list_organizations
list_people
list_locations
list_dates
unknown

User Question:
"{question}"

Intent:
"""

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response["message"]["content"].strip().lower()
    except Exception as e:
        print(f"[Intent Classifier Warning]: {e}")
        return "unknown"