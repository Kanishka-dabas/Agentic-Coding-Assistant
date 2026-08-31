"""
Session history endpoints - powers the sidebar list of past conversations
and lets the UI load a specific past conversation's full detail.
"""
from fastapi import APIRouter, HTTPException

from app.db.session import list_sessions
from app.memory.checkpointer import checkpointer

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("")
async def get_sessions():
    return list_sessions()


@router.get("/{thread_id}")
async def get_session_detail(thread_id: str):
    """
    Returns the full final state for one thread, so the UI can render
    that conversation's plan/code/execution result when resumed.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state = checkpointer.get(config)

    if state is None:
        raise HTTPException(status_code=404, detail="Session not found")

    values = state.get("channel_values", {})
    return {
        "task": values.get("task", ""),
        "current_step": values.get("current_step", ""),
        "result": values.get("result", ""),
        "plan": values.get("plan", []),
        "generated_code": values.get("generated_code", ""),
        "execution_success": values.get("execution_success"),
        "execution_stdout": values.get("execution_stdout", ""),
        "execution_stderr": values.get("execution_stderr", ""),
        "blocked": values.get("blocked", False),
        "block_reason": values.get("block_reason", ""),
    }