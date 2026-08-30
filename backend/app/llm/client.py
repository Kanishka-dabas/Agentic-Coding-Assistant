"""
Client for Groq's chat completions API.
"""

import requests

from app.core.config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq(system_prompt:str , user_message : str)->str:

    headers = {
        "Authorization" : f"Bearer {settings.Groq_api_key}" , 
        "Content-Type" : "application/json"
    }

    payload = {
        "model" : settings.Groq_model,
        "messages" : [
            {"role" : "system" , "content" : system_prompt},
            {"role" : "user" ,  "content" : user_message}
        ],
        "temperature" : 0.2
    }

    response = requests.post(GROQ_API_URL , headers=headers , json=payload , timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
