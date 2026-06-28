"""
State definition for the Account Intelligence Agent.

Defines AgentState — the shared TypedDict passed between all LangGraph nodes.
Every field that any node reads or writes must be declared here.

Imported by: nodes.py, graph.py
"""

from typing import TypedDict, Optional

class AgentState(TypedDict):
    company_name: str                   # the input query
    research_data: Optional[dict]       # what the tools returned (the raw facts)
    fit_label: Optional[str]            # what the score node decides
    fit_rationale: Optional[str]        # why the score node decided it
    brief: Optional[dict]               # the final structured output from write

