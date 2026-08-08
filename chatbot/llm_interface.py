import os
import json
import requests
import ollama
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

# Bypass system HTTP proxies for local Ollama requests
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

LOCAL_MODEL = "llama3.2:3b"



def ask_llm(prompt: str) -> str:
    """
    Cloud & Local Dual-Mode LLM Interface.
    Checks environment for Cloud API Keys (Groq, OpenAI, Gemini).
    Falls back to Local Ollama or Deterministic Knowledge Engine.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    # 1. Groq Cloud API (Free & Fast Cloud Llama-3.3)
    if groq_api_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Groq Cloud LLM Warning]: {e}")

    # 2. OpenAI Cloud API (GPT-4o-mini / GPT-3.5-Turbo)
    if openai_api_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[OpenAI Cloud LLM Warning]: {e}")

    # 3. Google Gemini Cloud API
    if gemini_api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[Gemini Cloud LLM Warning]: {e}")


    # 4. Local Ollama Fallback
    try:
        response = ollama.chat(
            model=LOCAL_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"[Ollama Service Warning]: {e}")
        return f"[OLLAMA_ERROR]: {e}"