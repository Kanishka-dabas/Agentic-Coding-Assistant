import os 
import json
import requests 

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def send_task(task : str) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/chat" ,
        json = {"task":task} , 
        timeout = 30
    )
    resp.raise_for_status()
    return resp.json() 


def send_task_streaming(task : str):
    """
    Generator that yields each step dict as it arrives from the backend's
    SSE endpoint, instead of returning once at the end like send_task().
    """
  
    resp = requests.post(
        f"{BACKEND_URL}/chat/stream",
        json = {"task" : task},
        stream = True,
        timeout = 60 
    )
    resp.raise_for_status()

    for line in resp.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if decoded.startswith("data:"):
            payload = decoded[len("data:"):]
            yield json.loads(payload)


def send_resume_streaming(thread_id:str , decision : str):
    resp = requests.post(
        f"{BACKEND_URL}/chat/resume",
        json = {"thread_id" : thread_id , "decision" : decision},
        stream = True,
        timeout=60
    )
    resp.raise_for_status()

    for line in resp.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if decoded.startswith("data:"):
            payload = decoded[len("data:"):]
            yield json.loads(payload)

def get_sessions() -> list:
    resp = requests.get(f"{BACKEND_URL}/sessions", timeout=10)
    resp.raise_for_status()
    return resp.json()            
