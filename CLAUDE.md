# CLAUDE.md

## Project
Account Intelligence Agent: a multi-tool agent that does an SDR's account
research and qualification in seconds. Every claim in its brief links back
to the source it came from.

Project structure and architecture: see README.md.

## Commands
- Activate venv (PowerShell): `.\.venv\Scripts\Activate.ps1`
- Run the agent: `python main.py`
- Run tests: `python -m pytest`

## Conventions
- Python 3.14.0
- Private helpers start with an underscore (`_format_chunks`, `_find_source_url`).
  Tests import them by those exact names.
- Unit tests follow the mocking pattern in `/tests/test_news.py`.
- Unit tests never make real network calls or real `time.sleep` calls; mock both.

## Boundaries
- Propose a plan before editing anything. Wait for approval.
- Only create or edit the files named in the prompt.
- Never commit. The developer reviews every change and commits by hand.
- Never open, print, or copy `.env` or any API key.