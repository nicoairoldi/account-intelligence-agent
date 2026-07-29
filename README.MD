## ACCOUNT INTELLIGENCE AGENT

> **Status:** Active portfolio project, currently in Phase 2. See the Status section below for progress. Architecture diagrams, installation instructions, and a live demo will land in Phase 4.

As a sales rep I spend around 15-30 minutes researching a single company to qualify them as a prospect. These go into my notes and then I'll spend 15 minutes searching my notes before I make a call to a company. I've spent months doing this by hand. Pulling SEC filings, FCC license data, job postings, and news articles to identify buying signals. This agent will do it in seconds.

You give it a company name. It pulls public data from multiple sources — company website, recent news, job postings as hiring signal proxies, and SEC/EDGAR filings for public companies — scores the account against a configurable ICP, and returns a structured qualification brief with citations explaining the fit verdict.

Built to demonstrate:

- Stateful multi-tool agent orchestration with LangGraph
- RAG pipeline with pgvector for retrieved-context briefs
- Hand-labeled eval set with LangSmith tracing to measure brief quality
- Production deployment on Railway

Stack: Python · LangGraph · Claude API · pgvector · Neon Postgres · TypeScript/Express · Railway

## Status

Phase 0 complete: working single-tool agent with full tool-use loop (tool call → function execution → result returned to model → final response). Hardcoded data for now — real data sources coming in Phase 2.

Phase 1 complete: multi-tool agent loop with structured JSON qualification brief.
Research and synthesis deliberately separated into distinct API calls —
Maps directly to LangGraph nodes in Phase 2.

Phase 2 Working:
Set each step (research, score, write) in their own LangGraph nodes.
Each step is now modularized so it will be easier to spot failure and test.
Each step completes part of the shared state that flows through the graph, producing the final brief.
