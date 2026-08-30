
import uuid

from fastapi import APIRouter

from app.agent.graph import agent_graph
from app.api.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "task": request.task, "current_step": "", "result": "",
        "plan": [], "generated_code": "", "execution_success": None,
        "execution_stdout": "", "execution_stderr": "", "execution_timed_out": False,
        "blocked": False, "block_reason": "", "retry_count": 0, "reflection_feedback": "",
    }
    final_state = agent_graph.invoke(initial_state, config=config)
    return ChatResponse(
        current_step=final_state.get("current_step", ""),
        result=final_state.get("result", ""),
    )
