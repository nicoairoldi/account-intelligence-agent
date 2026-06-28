"""
Entry point for the Account Intelligence Agent.

Calls run_agent() with a company query and prints the resulting qualification brief.
Phase 2 will replace run_agent() with a graph.invoke() call.

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
    