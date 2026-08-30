from pydantic import BaseModel

class ResumeRequest(BaseModel):
    thread_id : str
    decision : str   #approve /reject
    