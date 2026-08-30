"""
Retriever node - runs after planner, before coder. Fetches relevant
code chunks from the existing codebase so the coder node can follow
established patterns instead of writing in a vacuum.
"""

from app.agent.state import AgentState
from app.rag.retriever import retrieve_context

def retriever_node(state:AgentState):
    try:
        results = retrieve_context(state["task"], top_k=3)
        return {
            "current_step": "retriever",
            "result": f"Retrieved {len(results)} relevant code chunk(s).",
            "retrieved_context": results,
        }
    except Exception as e:
        return {
            "current_step": "retriever",
            "result": f"Retrieval failed: {e}",
            "retrieved_context": [],
        }