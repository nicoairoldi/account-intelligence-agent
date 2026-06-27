import anthropic 

from dotenv import load_dotenv
import json

load_dotenv()

client = anthropic.Anthropic()

def get_company_info(company_name):
    return {"company": company_name, "industry": "Energy", "employees": 5000}

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[
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
        }
    ],
    messages=[{"role": "user", "content": "What info do we have for Evergy"}],
)

print(response)

if response.stop_reason == "tool_use": 
    for item in response.content:
        if isinstance(item, anthropic.types.ToolUseBlock):
            if item.name == "get_company_info":
                result = get_company_info(item.input["company_name"])
                second_response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    tools=[
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
                        }
                    ],  # same tools as before
                    messages=[
                        {"role": "user", "content": "What info do we have for Evergy"}, # 1. original user question
                        {"role": "assistant", "content": response.content}, # 2. assistant's tool_use response
                        {"role": "user", "content":[{ "type": "tool_result", "tool_use_id": item.id, "content": json.dumps(result)}]},    # 3. tool result
                    ]
                )


print(result)


print(second_response)