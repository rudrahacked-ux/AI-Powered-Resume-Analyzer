"""
llm_skill_extractor.py
---------------------
LLM-based skill extraction using OpenRouter
Returns STRICT JSON: { "skills": [...] }
"""

import requests
import json
import re

# ---------- CONFIG ----------
API_KEY = "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"

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3-8b-instruct"  # fast + accurate

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",   # required by OpenRouter
    "X-Title": "Resume Skill Extractor"
}

# ---------- CORE FUNCTION ----------
def extract_skills_llm(resume_text):
    prompt = f"""
You are a resume parsing engine.

Extract ALL technical skills, programming languages, tools,
frameworks, and soft skills from the resume text.

Return STRICT JSON ONLY:
{{"skills": ["skill1", "skill2"]}}

Resume Text:
{resume_text}
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Resume Skill Extractor"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    response = requests.post(API_URL, headers=headers, json=payload,timeout=30)
    print("LLM request sent")
    if response.status_code != 200:
        print("LLM API Error:", response.text)
        return []

    content = response.json()["choices"][0]["message"]["content"]
    print("LLM raw response:", content)
    
    try:
        import re
        json_text = re.search(r"\{.*\}", content, re.DOTALL).group()
        parsed = json.loads(json_text)
        return [s.lower().strip() for s in parsed.get("skills", [])]
    except Exception as e:
        print("LLM parsing error:", e)
        return []
