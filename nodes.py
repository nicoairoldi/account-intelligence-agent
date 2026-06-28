"""
Agent logic and node functions for the Account Intelligence Agent.

Currently contains run_agent() — the Phase 1 research loop and brief generation.
Phase 2 will split this into three LangGraph node functions: research, score, write.

Imports: anthropic, tools.py
Imported by: main.py (run_agent), graph.py (Phase 2 node functions)
"""

import anthropic
from tools import TOOLS, execute_tool

from dotenv import load_dotenv
import json

load_dotenv()

# --- Constants --- 
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
client = anthropic.Anthropic()

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

    