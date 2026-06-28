"""
Tool definitions and implementations for the Account Intelligence Agent.

Contains:
- TOOLS: tool schema list passed to the Anthropic API
- Tool functions: get_company_info, get_news, get_job_postings (hardcoded stubs, Phase 2 will replace)
- TOOL_REGISTRY: maps tool name strings to their implementing functions
- execute_tool: dispatcher that routes model tool calls to the correct function

Imported by: nodes.py
Note: Tool implementations are stubs. Real data sources added in Phase 2, Week 5.
"""

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
