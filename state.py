"""
State definition for the Account Intelligence Agent.

Defines AgentState — the shared TypedDict passed between all LangGraph nodes.
Every field that any node reads or writes must be declared here.

Imported by: nodes.py, graph.py
"""

from typing import TypedDict, Optional

class AgentState(TypedDict):
    company_name: str                       # the input query
    analysis_focus: Optional[str]           # e.g. "focus on telecom signals only"
    research_data: Optional[list]           # It's the full research conversation: inital user prompt, the model's turns, and the tool results.
    retrieved_chunks: Optional[list[dict]]  # Holds the chunks from the retrieval based on the query
    fit_label: Optional[str]                # what the score node decides
    fit_rationale: Optional[str]            # why the score node decided it
    brief: Optional[dict]                   # the final structured output from write
    invalid_citations: Optional[list[int]]  # citation numbers the model used that don't match any retrieved chunk
    