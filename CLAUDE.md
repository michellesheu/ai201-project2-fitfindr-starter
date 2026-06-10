# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the Gradio UI
python app.py

# Test the planning loop directly (CLI)
python agent.py

# Verify data loads correctly
python utils/data_loader.py

# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_tools.py -v

# Quick tool smoke test
python -c "from tools import search_listings; print(search_listings('vintage graphic tee', size=None, max_price=50))"
```

## Architecture

Three-layer pipeline: `app.py` → `agent.py` → `tools.py`, with `utils/data_loader.py` providing data access.

**Data flow:**
1. `app.py` — Gradio UI. `handle_query(user_query, wardrobe_choice)` calls `run_agent()` and maps the returned session dict to 3 output panel strings.
2. `agent.py` — Planning loop. `run_agent(query, wardrobe) → dict` initializes a session dict via `_new_session()`, parses the query, and orchestrates the three tools. Session dict is the single source of truth; keys: `query`, `parsed`, `search_results`, `selected_item`, `wardrobe`, `outfit_suggestion`, `fit_card`, `error`.
3. `tools.py` — Three standalone tools, each independently testable:
   - `search_listings(description, size, max_price)` — keyword-scores listings from `data/listings.json`, returns sorted `list[dict]` or `[]`
   - `suggest_outfit(new_item, wardrobe)` — LLM call (Groq), handles empty wardrobe
   - `create_fit_card(outfit, new_item)` — LLM call (Groq), returns caption string; guards empty `outfit`

**LLM:** Groq `llama-3.3-70b-versatile` via `GROQ_API_KEY` in `.env`. Client initialized in `_get_groq_client()` in `tools.py`.

**Error branching:** If `search_listings` returns `[]`, agent sets `session["error"]` and returns early — `suggest_outfit` and `create_fit_card` are NOT called with empty input.

## Key Constraints

- All tool stubs live in `tools.py` — do not create separate files per tool.
- `load_listings()` from `utils/data_loader.py` must be used in `search_listings`; do not re-implement file loading.
- `create_fit_card` takes `(outfit, new_item)` — both arguments (check stub signature).
- Tests go in `tests/test_tools.py`, covering at least one failure mode per tool.
- `planning.md` must be filled out before implementation and must contain a text-based architecture diagram (ASCII or mermaid fenced block — no images).
