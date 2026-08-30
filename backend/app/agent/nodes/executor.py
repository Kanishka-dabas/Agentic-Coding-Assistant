"""
Executor node - the graph-facing wrapper around sandbox.executor.run_code().

  - sandbox/executor.py knows HOW to run code safely (Docker details).
  - this file knows how that fits into the AGENT'S state/graph.
"""

from app.agent.state import AgentState
from app.sandbox.executor import run_code

def executor_node(state : AgentState)->dict:

    code_to_run = state.get('generated_code' , "")

    result = run_code(code_to_run)

    if result['timed_out']:
        summary = "Execution timed out."
    elif result['success'] :
        summary = "Execution succeeded."
    else :
        summary = "Execution failed."

    return {
        'current_step' : 'executor',
        'result' : summary ,
        'execution_success' : result['success'],
        'execution_stdout' : result['stdout'],
        'execution_stderr' : result['stderr'],
        'execution_timed_out' : result['timed_out']
    }             
