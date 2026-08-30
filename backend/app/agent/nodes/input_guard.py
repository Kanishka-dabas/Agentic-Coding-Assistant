"""
Input guard node - runs FIRST in the graph, before any other node.
Wraps guardrails.input_validator so a bad task never reaches planning,
coding, or execution.
"""

from app.agent.state import AgentState
from app.guardrails.input_validator import validate_input

def input_guard_node(state : AgentState):
    verdict = validate_input(state["task"])

    if verdict["safe"]:
        return {
            "current_step" : "input_guard" , 
            "result" : "Input validation passed" , 
            "blocked" : False ,
            "blocked_reason" : ""
        }
    return {
                "current_step" : "input_guard" , 
                "result" : "Input blocked by guardrail" , 
                "blocked" : True ,
                "blocked_reason" : verdict["reason"]
            }

        