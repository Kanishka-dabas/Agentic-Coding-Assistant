"""
Coder node - calls the LLM to generate actual Python code based on the
task and the plan produced by planner_node.
"""

from app.agent.state import AgentState
from app.agent.prompts.coder_prompt import CODER_SYSTEM_PROMPT
from app.llm.gateway import generate

def coder_node(state:AgentState):
    plan_text = "\n".join(f"{i}. {step}" for i , step in enumerate(state['plan'] , start=1))
    user_message = f"Task : {state['task']}\n\n Plan :\n {plan_text}"

    context = state.get("retrieved_context", [])
    if context:
        context_text = "\n\n".join(f"From {c['file']}:\n{c['text']}" for c in context)
        user_message += f"\n\nRelevant existing code for reference:\n{context_text}"

    feedback = state.get('reflection_feedback',"")
    if feedback:
        user_message += (
            f"\n\nYour previous attempt failed. Here is an analysis of what went wrong:\n{feedback}"
            f"\n\nPlease write a corrected version of the code."
        )

    try :
        code = generate(CODER_SYSTEM_PROMPT , user_message)
        return {
            "current_step" : "coder" , 
            "result" : "Code generated" if not feedback else "Corrected code generated.", 
            "generated_code" : code
        }
    except Exception as e:
        return{
            "current_step" : "coder",
            "result" : f"Code generation failed : {e}",
            "generated_code" : ""
        }
    