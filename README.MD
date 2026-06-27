##

ACCOUNT INTELLIGENCE AGENT

##

As a sales rep I spend around 15-30 minutes researching a single company to qualify them as a prospect. These go into my notes and then ill spend 15 minutes searching my notes before I make a call to a company. Ive spent months doing this by hand. Pulling SEC fillings, FCC licence data, job postings, and new articles to identify buying signals. This agent will do it in seconds.

You give it a company name. It pulls public data from multiple sources — company website, recent news, job postings as hiring signal proxies, and SEC/EDGAR filings for public companies — scores the account against a configurable ICP, and returns a structured qualification brief with citations explaining the fit verdict.
Built to demonstrate:

Stateful multi-tool agent orchestration with LangGraph
RAG pipeline with pgvector for retrieved-context briefs
Hand-labeled eval set with LangSmith tracing to measure brief quality
Production deployment on Railway

Stack: Python · LangGraph · Claude API · pgvector · Neon Postgres · TypeScript/Express · Railway

Build so far
The agent gets the message from the user and we call the LLM with the api , its given a tool to call based on what is asked.
It then calls the function it knows to call with the input given name and we return that to the LLM
Finally the LLM gives it to the user
