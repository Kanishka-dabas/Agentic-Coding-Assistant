"""
HITL resume endpoint - takes the human's approve/reject decision and
resumes the paused graph from exactly where hitl_approval_node called
interrupt(), using the same thread_id.
"""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langgraph.types import Command

from app.agent.graph import agent_graph
from app.api.schemas.hitl_schema import ResumeRequest
from app.api.routes.stream import node_output_to_payload

router = APIRouter(prefix="/chat", tags=["chat"])


def resume_event_generator(thread_id: str, decision: str):
    config = {"configurable": {"thread_id": thread_id}}

    for chunk in agent_graph.stream(Command(resume=decision), config=config):
        if "__interrupt__" in chunk:
            interrupt_obj = chunk["__interrupt__"][0]
            payload = {
                "step": "hitl_approval",
                "thread_id": thread_id,
                "requires_approval": True,
                "generated_code": interrupt_obj.value.get("generated_code", ""),
                "message": interrupt_obj.value.get("message", ""),
            }
            yield f"data: {json.dumps(payload)}\n\n"
            continue

        for node_name, node_output in chunk.items():
            payload = node_output_to_payload(node_name, node_output, thread_id)
            yield f"data: {json.dumps(payload)}\n\n"


@router.post("/resume")
async def chat_resume(request: ResumeRequest):
    return StreamingResponse(
        resume_event_generator(request.thread_id, request.decision),
        media_type="text/event-stream",
    )