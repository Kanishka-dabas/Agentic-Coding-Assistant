"""
Planner node - calls the LLM to break the task into a step-by-step plan,
before any code is written or executed.
"""

import json

from app.agent.state import AgentState
from app.agent.prompts.planner_prompt import PLANNER_SYSTEM_PROMPT
from app.llm.gateway import generate

def planner_node(state : AgentState):
    try:
        raw_response = generate(PLANNER_SYSTEM_PROMPT , state["task"])
        plan = json.loads(raw_response)

        if not isinstance(plan , list):
            raise ValueError("Expected a JSON array of steps")

        return {
            "current_step" : "planner" , 
            "result" : f"Plan created with {len(plan)} steps",
            "plan" : plan
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "current_step" : "planner" , 
            "result" : f"Planning failed {e}",
            "plan" : []
        }    