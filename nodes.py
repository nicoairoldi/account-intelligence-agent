"""
Agent logic and node functions for the Account Intelligence Agent.

Three LangGraph node functions: research, score, write.

Imports: anthropic, tools.py, state.py
Imported by: graph.py
"""

import anthropic
from tools import TOOLS, execute_tool
from state import AgentState

from dotenv import load_dotenv
import json

load_dotenv()

# --- Constants --- 
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
client = anthropic.Anthropic()

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
    brief_response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="""Read the research in the conversation and return ONLY two fields: fit_label and fit_rationale.
        Score based on these signals:
        - SCADA or Telecom job postings = strong buying signal
        - Company under 2000 employees = easier to break into
        - New telecom network builds and substation builds = strong buying signal
        fit_label must be 'good_fit', 'poor_fit', or 'neutral'.
        fit_rationale must be one sentence explaining the score.
        Do not return any other fields""",
        messages=state["research_data"],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "fit_label": {"type": "string"},
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
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="""You are a sales brief writer. Assemble a qualification brief from the research and the pre-determined 
        fit score. Do not re-score. Use exactly the fit_label and fit_rationale provided.""",
        messages=state["research_data"] + [
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
                        "fit_label": {"type": "string"},
                        "fit_rationale": {"type": "string"}
                    },
                    "required": ["company_name", "industry", "employees", "news_summary", "job_postings", "fit_label", "fit_rationale"],
                    "additionalProperties": False
                }
            }
        }
    )
    return {"brief": json.loads(response.content[0].text)}


# --- Agent loop ---
def run_agent(user_query: str) -> str:
    """
    Runs a single-turn agent loop for the given query.

    Sends the query to the model, checks if it requests a tool call,
    executes the tool via execute_tool(), and sends the result back
    to get a final natural language response.

    Args:
        user_query: The raw input string from the caller.

    Returns:
        The model's final response as a plain string.
    """
    # 1. First API call — send the query
    messages = [{"role": "user", "content": user_query}]
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

    brief_response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="""You are a sales intelligence assistant. Using the research in the conversation, 
        return a qualification brief as JSON. Be concise. 
        Generate a qualification brief. For fit_label use 'good_fit', 'poor_fit', or 'neutral'.
        Score based on these signals:
        - SCADA or Telecom job postings = strong buying signal
        - Company under 2000 employees = easier to break into
        - New telecom network builds and substation builds = strong buying signal,  
        Use fit_label: good_fit, poor_fit, or neutral""",
        messages=messages,
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
                        "fit_label": {"type": "string"},
                        "fit_rationale": {"type": "string"}
                    },
                    "required": ["company_name", "industry", "employees", "news_summary", "job_postings"],
                    "additionalProperties": False
                }
            }
        }
    )
    return json.loads(brief_response.content[0].text)

    