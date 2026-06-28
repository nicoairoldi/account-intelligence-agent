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
        {
            "name": "get_news",
            "description": "finds current and relevant news articles about the company",
            "input_schema": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "name of the company",
                    },
                },
                "required": ["company_name"],
            }
        },
        {
            "name": "get_job_postings",
            "description": "finds current jobs postings from the company",
            "input_schema": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "name of the company",
                    },
                },
                "required": ["company_name"],
            }
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

def get_news(company_name: str) -> dict:
    """
    Returns hardcoded company data for a given company name.

    Args:
        company_name: The name of the company to look up.

    Returns:
        A object with keys: company and articles

    Note:
        Hardcoded stub — will be replaced with a real data source in Phase 2.
    """
    return {
        "company" : company_name,
        "articles": [
            {"headline": "Evergy announces new substation builds", "date": "2026-06-01"},
            {"headline": "Evergy to invest in 5G network", "date": "2026-04-15"}
        ]
    }

def get_job_postings(company_name: str)-> dict:
    """
    Returns hardcoded company data for a given company name.

    Args:
        company_name: The name of the company to look up.

    Returns:
        A object with keys: company and articles

    Note:
        Hardcoded stub — will be replaced with a real data source in Phase 2.
    """
    return {
        "company": company_name,
        "listed_jobs": [
            {"Position": "SCADA Engineer", "Description": " Responsible for designing, implementing, and maintaining the computer systems used to monitor and control industrial processes in real-time. "},
            {"Position": "Telecom Engineer", "Description": " Responsible for designing, implementing, and maintaining the systems and networks that enable reliable voice, data, and video communication. "},
        ]
    }


TOOL_REGISTRY = {
    "get_company_info": get_company_info,
    "get_news": get_news,
    "get_job_postings": get_job_postings
}

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
    fn = TOOL_REGISTRY.get(tool_name)
    if fn is None:
        raise ValueError(f"Unknown tool: {tool_name}")
        # **tool_input makes the dict turn into get_company_info(company_name="Evergy")
    return fn(**tool_input)

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

    
                
    
# --- Entry point ---
if __name__ == "__main__":
    result = run_agent("Tell me all info do we have for Evergy")
    print(result)