from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings

_checkpointer_cm = PostgresSaver.from_conn_string(settings.postgres_url)
checkpointer = _checkpointer_cm.__enter__()
checkpointer.setup()