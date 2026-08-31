"""
Runs the agent against EVAL_TASKS and scores each result's PLAN and
GENERATED CODE using an LLM-as-judge, since exact-output assertions
don't work well for non-deterministic LLM-generated code.

Execution success is intentionally NOT scored here - it depends on the
local Docker/sandbox environment (Windows vs. containerized deployment
handle temp paths differently), so it's verified manually via the UI
instead. This keeps the eval focused on planning/coding quality, which
is consistent across environments.

Usage (from backend/, with the venv active):
    uv run python -m tests.eval.run_eval

Or inside the deployed container:
    docker compose exec backend python -m tests.eval.run_eval
"""
import json
import sys
import os
import uuid
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from langgraph.types import Command

from app.agent.graph import agent_graph
from app.llm.gateway import generate
from tests.eval.test_cases import EVAL_TASKS
from tests.eval.judge_prompt import JUDGE_SYSTEM_PROMPT


def run_agent_on_task(task: str) -> dict:
    """
    Runs the full graph for one task, auto-approving any HITL interrupt.
    Returns the FULL accumulated state via get_state, not just the last
    node's partial output (chunk.values() during streaming only gives
    each node's own returned keys, which would drop earlier fields like
    generated_code once a later node runs).
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "task": task, "current_step": "", "result": "",
        "plan": [], "retrieved_context": [], "generated_code": "",
        "execution_success": None, "execution_stdout": "", "execution_stderr": "",
        "execution_timed_out": False, "blocked": False, "block_reason": "",
        "retry_count": 0, "reflection_feedback": "",
    }

    for chunk in agent_graph.stream(initial_state, config=config):
        if "__interrupt__" in chunk:
            for _ in agent_graph.stream(Command(resume="approve"), config=config):
                pass

    return agent_graph.get_state(config).values


def judge_result(task: str, code: str) -> dict:
    user_message = f"Task: {task}\n\nGenerated code:\n{code}"
    try:
        raw = generate(JUDGE_SYSTEM_PROMPT, user_message)
        return json.loads(raw)
    except Exception as e:
        return {"score": 0, "reasoning": f"Judge failed: {e}"}


def run_eval():
    results = []

    for task in EVAL_TASKS:
        print(f"Running: {task}")
        final_state = run_agent_on_task(task)

        code = final_state.get("generated_code", "")

        judgment = judge_result(task, code)
        results.append({
            "task": task,
            "score": judgment.get("score", 0),
            "reasoning": judgment.get("reasoning", ""),
        })
        print(f"  -> score: {judgment.get('score')}/5 - {judgment.get('reasoning')}")

        time.sleep(5)  # avoid hitting Groq's per-minute rate limit

    print("\n=== Evaluation Summary ===")
    avg_score = sum(r["score"] for r in results) / len(results)
    print(f"Average judge score: {avg_score:.1f}/5")

    return results


if __name__ == "__main__":
    run_eval()