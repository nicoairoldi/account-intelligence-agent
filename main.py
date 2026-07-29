"""
Entry point for the Account Intelligence Agent.

Calls copioled.invoke() with a company name and optionally analysis focus  
Invoke walks the graph: START → research → score → write → END 
After write returns END LangGraph hands the final state back which includes our brief.


Usage: python main.py
"""

from graph import compiled

# --- Entry point ---
if __name__ == "__main__":
    company_name = input("Enter a company name: ")
    focus = input("Enter analysis focus (or press enter to skip): ")
    result = compiled.invoke({
        "company_name": company_name,
        "analysis_focus": focus if focus else None,
        "research_data": None,
        "fit_label": None,
        "fit_rationale": None,
        "brief": None
    })
    print(result["brief"])
    