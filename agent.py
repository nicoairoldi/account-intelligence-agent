"""
Account Intelligence Agent — Phase 1

Single-agent loop using the Anthropic Python SDK with hardcoded tool implementations.
Entry point: run_agent(user_query) -> str

Phase 2 will replace hardcoded tools with real data sources and migrate to LangGraph.
"""

import anthropic 

from dotenv import load_dotenv
import json

load_dotenv()

# --- Constants --- 
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# --- Tool definitions ---
TOOLS = [
        {
            "name": "get_company_info",
            "description" : "finds the info of the given company",
            "input_schema": {
                "type" : "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description" : "name of the company",
                    },
                },
                "required": ["company_name"],
            },
        },
    ]


client = anthropic.Anthropic()


# --- Tool implementations ---
def get_company_info(company_name: str) -> dict:
    """
    Returns hardcoded company data for a given company name.

    Args:
        company_name: The name of the company to look up.

    Returns:
        A dict with keys: company, industry, employees.

    Note:
        Hardcoded stub — will be replaced with a real data source in Phase 2.
    """
    return {"company": company_name, "industry": "Energy", "employees": 5000}

# --- Tool dispatcher ---
def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Routes a tool call from the model to the correct Python function.

    Args:
        tool_name: The name of the tool the model selected.
        tool_input: The arguments the model passed to the tool.

    Returns:
        The result dict from the called tool implementation.

    Raises:
        ValueError: If tool_name does not match any known tool.
    """
    if tool_name == "get_company_info":
        return get_company_info(tool_input["company_name"])
    raise ValueError(f"Unknown tool: {tool_name}")

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
    response = client.messages.create(
    model= MODEL,
    max_tokens = MAX_TOKENS,
    tools=TOOLS,
    messages=[{"role": "user", "content": user_query}],
)
    # 2. Check if model wants to use a tool
    if response.stop_reason == "tool_use": 
        for item in response.content:
            if isinstance(item, anthropic.types.ToolUseBlock):
                if item.name == "get_company_info":
                    result = execute_tool(item.name, item.input)
                    # 3. Second API call — send tool result back
                    second_response = client.messages.create(
                        model=MODEL,
                        max_tokens=MAX_TOKENS,
                        tools=TOOLS,  
                        messages=[
                            {"role": "user", "content": user_query}, # 1. original user question
                            {"role": "assistant", "content": response.content}, # 2. assistant's tool_use response
                            {"role": "user", "content":[{ "type": "tool_result", "tool_use_id": item.id, "content": json.dumps(result)}]},    # 3. tool result
                        ]
                    )
                    return(second_response.content[0].text)

# --- Entry point ---
if __name__ == "__main__":
    result = run_agent("What info do we have for Evergy")
    print(result)