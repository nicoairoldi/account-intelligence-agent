"""
LangGraph graph construction for the Account Intelligence Agent.

Defines and compiles the StateGraph: research → score → write.
Exposes the compiled graph for invocation via main.py.

Imports: langgraph, state.py, nodes.py
Imported by: main.py
"""

from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import research, score, write

graph = StateGraph(state_schema=AgentState)
# nodes
graph.add_node("research", research)
graph.add_node("score", score)
graph.add_node("write", write)

# edges
graph.add_edge(START, "research")
graph.add_edge("research", "score")
graph.add_edge("score", "write")
graph.add_edge("write", END)
compiled = graph.compile()