"""
Main Orchestration Graph
"""

from langgraph.graph import StateGraph , START , END
from app.memory.checkpointer import checkpointer

from app.agent.state import AgentState
from app.agent.nodes.input_guard import input_guard_node
from app.agent.nodes.planner import planner_node
from app.agent.nodes.retriever import retriever_node
from app.agent.nodes.coder import coder_node
from app.agent.nodes.code_guard import code_guard_node
from app.agent.nodes.hitl import hitl_approval_node
from app.agent.nodes.executor import executor_node
from app.agent.nodes.reflector import reflector_node
from app.agent.routing import route_after_input_guard , route_after_code_guard , route_after_executor , route_after_hitl


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node('input_guard' , input_guard_node)
    graph.add_node('planner' , planner_node)
    graph.add_node('retriever' , retriever_node)
    graph.add_node('coder' , coder_node)
    graph.add_node('code_guard' , code_guard_node)
    graph.add_node('hitl_approval' , hitl_approval_node)
    graph.add_node('executor' , executor_node)
    graph.add_node('reflector' , reflector_node)

    graph.add_edge(START , 'input_guard')
    graph.add_conditional_edges('input_guard' , route_after_input_guard, {"proceed":"planner" , "end" : END})
    graph.add_edge("planner" , "retriever")
    graph.add_edge("retriever" , "coder")
    graph.add_edge("coder" , "code_guard")
    graph.add_conditional_edges('code_guard' , route_after_code_guard, {"proceed":"hitl_approval" , "end" : END})
    graph.add_conditional_edges('hitl_approval' , route_after_hitl ,{"proceed" : "executor" , "end" : END})
    graph.add_conditional_edges("executor" , route_after_executor , {"end":END , "retry":"reflector" , "escalate" : END})
    graph.add_edge('reflector' , 'coder')

    return graph.compile(checkpointer=checkpointer)


# Compiled once at import time and reused across requests — recompiling per-request would work but wastes cycles for no benefit since the graph shape doesn't change at runtime.
agent_graph = build_graph()
