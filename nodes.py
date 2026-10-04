"""
Agent logic and node functions for the Account Intelligence Agent.

Three LangGraph node functions: research, score, write.

Imports: anthropic, tools.py, state.py
Imported by: graph.py
"""

import anthropic
from tools import TOOLS, execute_tool
from state import AgentState
from rag.retrieve import retrieve_chunks
import re 

from dotenv import load_dotenv
import json

load_dotenv()

# --- Constants --- 
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
client = anthropic.Anthropic()

def _format_chunks(chunks: list[dict])-> str:
    """
    Formats the returned chunks to be a string for the model to read
    """
    chunk_list = []
    for i, row in enumerate(chunks):
        to_add = f"[Source {i+1}]: {row['title']} - {row['source_name']}, {row['published_at']}\n{row['chunk_text']}"
        chunk_list.append(to_add)
    return "\n\n".join(chunk_list)

def _extract_source_numbers(source_str: str) -> list[int]:
    """
    scan a string for every [Source #] instance and return what number it has 
    """
    return list(map(int, re.findall(r"\[Source (\d+)\]", source_str)))

def _find_source_url(tag_numbers: list[int], chunks: list[dict]) -> dict:
    """
    take the tag list, find the article metadata for each tag, handle the bad tags, and group the results by URL.
    """
    entries_by_url = {}
    invalid_tags = []
    for src in tag_numbers:
        if src > 0 and src <= 5:
            chunk = chunks[src-1]
            if chunk["url"] not in entries_by_url:
                entries_by_url[chunk["url"]] = {"title": chunk["title"], "source_name": chunk["source_name"], "url": chunk["url"], "published_at": chunk["published_at"],"tags": [src]}
            else:
                if src not in entries_by_url[chunk["url"]]["tags"]:
                    entries_by_url[chunk["url"]]["tags"].append(src)
        else: 
            invalid_tags.append(src)
    return {"sources": list(entries_by_url.values()), "invalid_tags": invalid_tags}

def research(state: AgentState) -> dict:
    """
    Reads the company name from state
    Runs the tool loop using that name
    returns research data: everything the tools return 
    """
    # 1. First API call — send the query
    content = state["company_name"]
    if state["analysis_focus"]:
        content += f". Analysis focus: {state["analysis_focus"]}"
    messages = [{"role": "user", "content": content}]
    response = client.messages.create(
        model= MODEL,
        max_tokens = MAX_TOKENS,
        tools=TOOLS,
        messages=messages,
    )

    # 2. Check if model wants to use a tool
    while response.stop_reason != "end_turn":
        messages.append({"role": "assistant", "content": response.content}) 
        for item in response.content:
            if isinstance(item, anthropic.types.ToolUseBlock):
                result = execute_tool(item.name, item.input)
                messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": item.id, "content": json.dumps(result)}]})
        # 3. Second API call — send tool result back  
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=TOOLS,  
            messages = messages
        )

    return {"research_data": messages}

def score(state: AgentState) -> dict:
    """
    Reads research_data from state.
    Calls the model to evaluate fit against ICP scoring signals.
    Returns fit_label and fit_rationale only. 
    """
    message = state["research_data"].copy()
    message.append({"role": "user", "content": _format_chunks(state["retrieved_chunks"])})
    brief_response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="""Read the research and the retrieved_context in the conversation and return ONLY two fields: fit_label and fit_rationale.
        Score based on these signals:
        - SCADA or Telecom job postings = strong buying signal
        - Company under 2000 employees = easier to break into
        - New telecom network builds and substation builds = strong buying signal
        fit_label must be 'good_fit', 'poor_fit', or 'neutral'.
        fit_rationale must be one sentence explaining the score.
        Do not return any other fields
        Base your analysis only on the provided research and context. If the context doesn't contain enough information, say so rather than speculating.""",
        messages=message,
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "fit_label": {"type": "string", "enum": ["good_fit", "poor_fit", "neutral"]},
                        "fit_rationale": {"type": "string"}
                    },
                    "required": ["fit_label", "fit_rationale"],
                    "additionalProperties": False
                }
            }
        }
    )

    parsed = json.loads(brief_response.content[0].text)
    return {
        "fit_label": parsed["fit_label"],
        "fit_rationale": parsed["fit_rationale"]
    }

def write(state: AgentState)-> dict:
    """
    Writes brief to state based on research_data, fit_label, and fit_rationale
    Returns the brief
    """
    message = state["research_data"].copy()
    message.append({"role": "user", "content": _format_chunks(state["retrieved_chunks"])})
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="""You are a sales brief writer. Assemble a qualification brief from the research, retrieved context and the pre-determined 
        fit score. Do not re-score. Use exactly the fit_label and fit_rationale provided. Base your analysis only on the provided research and context. 
        If the context doesn't contain enough information, say so rather than speculating. 
        In news_summary, cite every factual claim with its source tag in exactly this format: [Source N], using the numbers shown on the context blocks. 
        Only use source numbers that appear in the provided context. Use one number per tag; if a claim has multiple sources, 
        write separate tags like [Source 1][Source 3]. Do not include URLs.""",
        messages=message + [
            {
                "role": "user", 
                "content": f"Fit score already determined: fit_label={state['fit_label']}, fit_rationale={state['fit_rationale']}. Assemble the final brief using this score and the research above."
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "company_name": {"type": "string"},
                        "industry": {"type": "string"},
                        "employees": {"type": "integer"},
                        "news_summary": {"type": "string"},
                        "job_postings": {"type": "array"},
                        "fit_label": {"type": "string", "enum": ["good_fit", "poor_fit", "neutral"]},
                        "fit_rationale": {"type": "string"}
                    },
                    "required": ["company_name", "industry", "employees", "news_summary", "job_postings", "fit_label", "fit_rationale"],
                    "additionalProperties": False
                }
            }
        }
    )
    brief = json.loads(response.content[0].text)
    tag_numbers = _extract_source_numbers(brief["news_summary"])
    src_urls = _find_source_url(tag_numbers, state["retrieved_chunks"])
    brief["sources"] = src_urls["sources"]
    return {"brief": brief, "invalid_citations":src_urls["invalid_tags"] }

def retrieve(state: AgentState) -> dict:
    """
    Writes the retrieved data based on the query and company name back to state
    """
    query = f"Latest news and financial performance of {state["company_name"]}"
    if state["analysis_focus"]:
        query += f". Analysis focus: {state["analysis_focus"]}"

    retrieval_list = retrieve_chunks(query, state["company_name"])
    return {"retrieved_chunks": retrieval_list}

