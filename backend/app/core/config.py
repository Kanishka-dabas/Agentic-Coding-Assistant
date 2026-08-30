"""
Centralized settings, loaded from environment variables / .env.

Every other module should import `settings` from here rather than calling
os.getenv() directly. This keeps config in one auditable place, gives us
type validation for free, and makes it trivial to point at a different
.env per environment (local / CI / AKS).
"""

from pydantic_settings import BaseSettings , SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env" , extra="ignore")

    #app
    app_name : str ="Agentic-Coding-Assistant"
    environment : str ='local'

    #llm
    Groq_api_key : str =""
    Groq_model : str = "openai/gpt-oss-120b"

    #api-server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    postgres_url: str = "postgresql://postgres:postgres@localhost:5432/agentic"



@lru_cache
def get_settings()->Settings:
    """
    Cached so we parse env vars once per process, not once per request.
    """
    return Settings()

settings = get_settings()