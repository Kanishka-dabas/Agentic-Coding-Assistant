from pydantic import BaseModel , Field

class ChatRequest(BaseModel):
    task : str = Field(... , min_length=1 , description="The coding task the user wants the agent to perform")

class ChatResponse(BaseModel):
    current_step :str
    result : str    