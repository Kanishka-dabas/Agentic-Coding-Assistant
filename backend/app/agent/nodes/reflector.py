"""
Reflector node - runs when execution fails. Calls the LLM to analyze the
error and produce a fix suggestion, which the coder node will use on the
next attempt. Also increments retry_count, which the retry_limiter
guardrail checks via routing.py.
"""

from app.agent.state import AgentState
from app.agent.prompts.reflector_prompt import REFLECTOR_SYSTEM_PROMPT
from app.llm.gateway import generate

def reflector_node(state:AgentState):
    user_message = (f"Task : {state['task']}\n\n"
                    f"Code: \n {state.get('generated_code' , '')}\n\n"
                    f"Error: \n {state.get('execution_stderr' , '')}")

    try :
        feedback = generate(REFLECTOR_SYSTEM_PROMPT , user_message)

    except Exception as e:
        feedback = f"Reflection failed : {e}"

    new_retry_count = state.get('retry_count' ,0)+1

    return {
        "current_step": "reflector",
        "result": f"Reflection (attempt {new_retry_count}): {feedback}",
        "reflection_feedback": feedback,
        "retry_count": new_retry_count,
    }
    
        

      