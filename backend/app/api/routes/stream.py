"""
SSE streaming endpoint - HITL-aware.

Each new task gets a unique thread_id, which the checkpointer uses to
track this specific graph run's paused state. When the graph hits the
hitl_approval interrupt, we send a special payload (requires_approval)
and stop - the frontend must call /chat/resume with the same thread_id
and the human's decision to continue.
"""

import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.graph import agent_graph
from app.api.schemas.chat_schema import ChatRequest

router = APIRouter(prefix="/chat" , tags=["chat"])

def node_output_to_payload(node_name:str , node_output:dict , thread_id:str)->str:
    return {
        "step": node_name,
        "thread_id": thread_id,
        "current_step": node_output.get("current_step", ""),
        "result": node_output.get("result", ""),
        "plan": node_output.get("plan", []),
        "generated_code": node_output.get("generated_code", ""),
        "execution_success": node_output.get("execution_success", None),
        "execution_stdout": node_output.get("execution_stdout", ""),
        "execution_stderr": node_output.get("execution_stderr", ""),
        "blocked": node_output.get("blocked", False),
        "block_reason": node_output.get("block_reason", ""),
        "retry_count": node_output.get("retry_count", None),
    }

def event_generator(task:str):
    thread_id = str(uuid.uuid4())
    config = {'configurable' : {'thread_id':thread_id}}

    initial_state = {
        "task": task,
        "current_step": "",
        "result": "",
        "plan": [],
        "generated_code": "",
        "execution_success": None,
        "execution_stdout": "",
        "execution_stderr": "",
        "execution_timed_out": False,
        "blocked": False,
        "block_reason": "",
        "retry_count": 0,
        "reflection_feedback": "",
    }

    for chunk in agent_graph.stream(initial_state , config=config):
        if "__interrupt__" in chunk :
            interrupt_obj = chunk["__interrupt__"][0]
            payload = {
                "step" : "hitl approval",
                "thread_id" : thread_id ,
                "requires_approval" : True ,
                "generated_code" : interrupt_obj.value.get("generated_code" , ""),
                "message" : interrupt_obj.value.get("message","")
            }
            yield f"data: {json.dumps(payload)}\n\n"
            continue

        for node_name , node_output in chunk.items():
            payload = node_output_to_payload(node_name , node_output , thread_id)
            yield f"data: {json.dumps(payload)}\n\n"


@router.post("/stream")
async def chat_stream(request : ChatRequest):
    return StreamingResponse(event_generator(request.task) , media_type="text/event-stream")
