"""
Entry point for the Account Intelligence Agent.

Calls run_agent() with a company query and prints the resulting qualification brief.
Phase 2 will replace run_agent() with a graph.invoke() call.

Usage: python main.py
"""

from nodes import run_agent

# --- Entry point ---
if __name__ == "__main__":
    result = run_agent("Tell me all info do we have for Evergy")
    print(result)