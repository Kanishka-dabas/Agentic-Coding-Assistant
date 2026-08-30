"""
Routing functions - decide which node runs next based on current state.
"""

from app.agent.state import AgentState
from app.guardrails.retry_limiter import has_retries_left

def route_after_input_guard(state : AgentState)->str:
    if state.get("blocked"):
        return "end"
    return "proceed"

def route_after_code_guard(state: AgentState) -> str:
    if state.get("blocked"):
        return "end"
    return "proceed"

def route_after_executor(state : AgentState) -> str:
    """
    If execution succeeded, we're done. If it failed, check the retry
    limiter guardrail: retry via the reflector if attempts remain,
    otherwise escalate (end) rather than loop forever.
    """
    if state.get("execution_success"):
        return "end"
    if has_retries_left(state.get('retry_count' , 0)):
        return "retry"
    return "escalate"

def route_after_hitl(state : AgentState)->str:
    if state.get("blocked"):
        return "end"
    return "proceed"

