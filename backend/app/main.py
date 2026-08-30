from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import chat , health , stream , hitl , sessions

app = FastAPI(title=settings.app_name)

app.include_router(chat.router)
app.include_router(health.router)
app.include_router(stream.router)
app.include_router(hitl.router)
app.include_router(sessions.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app" , host=settings.backend_host , port = settings.backened_post , reload = True)