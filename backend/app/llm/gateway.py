"""
LLM gateway - the single place every node calls to talk to an LLM.
"""

from app.llm.client import call_groq

def generate(system_prompt:str , user_message:str)->str:
    return call_groq(system_prompt , user_message)