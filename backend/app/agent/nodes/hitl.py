"""
HITL approval node - pauses the graph and waits for a human decision
before generated code is allowed to execute.
"""

from langgraph.types import interrupt

from app.agent.state import AgentState

def hitl_approval_node(state:AgentState):
    decision = interrupt({
        "generated_code" : state.get('generated_code' , ""),
        "message" : "Approve this code for execution ?"
    })
    if decision == "approve":
        return {
            "current_step" : "hitl approval",
            "result":"Human approved execution",
            "blocked" : False,
            "block_reason":""
        }
    else:
        return {
                    "current_step" : "hitl approval",
                    "result":"Human rejected execution",
                    "blocked" : True,
                    "block_reason":"Rejected by human reviewer."
                }
    