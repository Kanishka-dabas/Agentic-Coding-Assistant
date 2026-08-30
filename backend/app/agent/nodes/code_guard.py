"""
Code guard node - runs after input_guard, before executor.
Wraps guardrails.code_scanner so dangerous code never reaches the sandbox.
"""

from app.agent.state import AgentState
from app.guardrails.code_scanner import scan_code

def code_guard_node(state : AgentState):
    code_to_scan = state.get('generated_code' , "") 

    verdict = scan_code(code_to_scan)

    if verdict["safe"]:
        return {
            "current_step": "code_guard",
            "result": "Code scan passed.",
            "blocked": False,
            "block_reason": "",
        }
    else:
        return {
            "current_step": "code_guard",
            "result": "Code blocked by guardrail.",
            "blocked": True,
            "block_reason": verdict["reason"],
        }
    