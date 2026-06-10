# FitFindr — Project 2 Milestones

**Due: Sunday June 14, 2026 at 11:59PM PDT** | ~8–9 hours total

---

## Milestone 1: Explore the Starter Repo (~30 min)

- [ ] Read `data/listings.json` — note fields: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`
- [ ] Read `data/wardrobe_schema.json` — note fields available on each wardrobe item
- [ ] Read `utils/data_loader.py` — understand `load_listings()`, `get_example_wardrobe()`, `get_empty_wardrobe()`
- [ ] Write 2–3 sentence FitFindr description in `planning.md` "A Complete Interaction" section (what triggers each tool, what happens when something fails)

**Checkpoint:** Can describe listings data structure from memory. Understand difference between `get_example_wardrobe()` and `get_empty_wardrobe()`.

---

## Milestone 2: Write Your Spec Before Any Code (~1 hour)

- [ ] Open `planning.md` and fill in each section with specific, implementation-ready content
- [ ] For each of the 3 required tools, fill in: what it does, exact input parameters (name, type, meaning), what it returns, what agent does if it fails
- [ ] Planning loop section: specific conditional logic (e.g. "if `search_listings` returns empty, set error in session and return early — do NOT call `suggest_outfit`")
- [ ] Draw agent architecture diagram in `## Architecture` section — **must be text-based** (ASCII art or ` ```mermaid ` fenced block), NOT an image
- [ ] Fill in `## AI Tool Plan` — for each tool: which AI used, what input given, expected output, how you'll verify before running
- [ ] Trace the example query step-by-step through all 3 tools in the "Complete Interaction" section
- [ ] Review each error handling row — responses must be specific and actionable

**Checkpoint:** `planning.md` describes all 3 tools with specific inputs/return values, planning loop describes conditional logic, diagram shows data/control flow, complete interaction traced step-by-step.

---

## Milestone 3: Build and Test Each Tool in Isolation (~2–3 hours)

- [ ] Open `tools.py` — stubs already there, implement each function (do NOT create separate files)
- [ ] Implement `search_listings(description, size, max_price)`:
  - Use `load_listings()` from `utils/data_loader.py`
  - Return `[]` when no matches — no exception
- [ ] Implement `suggest_outfit(new_item, wardrobe)`:
  - Call Groq LLM (`llama-3.3-70b-versatile`) with `GROQ_API_KEY` from `.env`
  - Handle empty wardrobe (`wardrobe['items']` is empty) — return useful general advice, not crash
- [ ] Implement `create_fit_card(outfit, new_item)`:
  - Call Groq LLM
  - Guard against empty `outfit` string — return error message string, not Python exception
  - Verify outputs vary for same input (increase temperature if identical)
- [ ] Create `tests/test_tools.py` — at least 1 test per failure mode for each tool
- [ ] Run `pytest tests/` — all tests pass before moving to M4

**Checkpoint:** Each tool callable with test inputs, returns sensible output. Each failure mode returns specific informative message rather than exception.

---

## Milestone 4: Wire Up the Planning Loop and State (~2 hours)

- [ ] Open `agent.py` — session dict and `run_agent()` signature pre-built, read TODO steps
- [ ] Implement `run_agent()` following the numbered steps, matching your `planning.md` Planning Loop section
- [ ] Implement `handle_query()` in `app.py` — call `run_agent()`, map session dict to 3 output panel strings
- [ ] Run complete interaction using example query from `planning.md`:
  - Print `session["selected_item"]` → confirm it's the exact dict passed to `suggest_outfit`
  - Print `session["outfit_suggestion"]` → confirm it's what went into `create_fit_card`
- [ ] Test branch path: run with impossible query → confirm `session["error"]` set, `session["fit_card"]` is `None`, `suggest_outfit` NOT called

**Checkpoint:** Complete query flows through all 3 tools with state visibly passing. Agent behavior differs for empty vs non-empty `search_listings` results.

---

## Milestone 5: Test Every Failure Mode Deliberately (~1 hour)

- [ ] Trigger `search_listings` returning zero results — confirm returns `[]` without exception; confirm full agent tells user what failed and what to try next (not just "no results found")
- [ ] Trigger `suggest_outfit` with empty wardrobe — confirm returns useful string (not exception)
- [ ] Trigger `create_fit_card` with empty outfit string — confirm returns descriptive error string (not Python exception)
- [ ] Screenshot or record at least one triggered failure to include in demo video

**Checkpoint:** All 3 failure modes trigger deliberately and produce specific, informative agent responses. At least 1 documented failure for demo.

---

## Milestone 6: Document and Record (~1–1.5 hours)

- [ ] Run `python app.py` and test end-to-end (check terminal URL — may not be `localhost:7860`)
- [ ] Confirm all 3 output panels populate correctly for happy-path query
- [ ] Write `README.md` covering all required sections:
  - Tool inventory: name, inputs (param names + types), outputs, purpose
  - How the planning loop works (conditional logic, not just "decides what to do")
  - State management: what's stored, when, how passed between tools
  - Error handling per tool with at least 1 concrete example from testing
  - Spec reflection: 1 way spec helped, 1 way implementation diverged and why
  - AI usage: at least 2 specific instances (what you gave AI, what it produced, what you changed)
- [ ] Record 3–5 min demo video showing:
  - Complete multi-step interaction from user query to fit card (all 3 tools)
  - Narration of what agent is doing at each step
  - State visibly or verbally passing between tools
  - At least 1 triggered failure with graceful, informative response

**Checkpoint:** App runs at localhost, all output panels populate. README covers all sections with substantive content. Demo recorded.

---

## Required Features (graded)

- [ ] 3+ tools with defined interfaces (`search_listings`, `suggest_outfit`, `create_fit_card`)
- [ ] Planning loop — responds to what was returned, not fixed sequence
- [ ] State management — results flow between tools without user re-entry
- [ ] Error handling per tool — specific messages, no silent fail or crash
- [ ] Multi-step workflow using all 3 tools in sequence

---

## Stretch Features (extra credit — update `planning.md` first)

- [ ] Price comparison tool: estimates if price is fair vs comparable listings
- [ ] Style profile memory: remember user preferences across sessions
- [ ] Trend awareness: check recent posts/tags for popular styles in user's size range
- [ ] Retry with fallback: if `search_listings` returns nothing, auto-retry with loosened constraints

---

## Submission (via Course Portal)

- [ ] Link to forked GitHub repository
- [ ] `planning.md` in repo root (written before implementation, updated before stretch features)
- [ ] `README.md` with all required sections
- [ ] Demo video (3–5 minutes)

---

## Setup

```bash
# Clone your fork, then:
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
pip install -r requirements.txt

# Create .env (never commit this)
echo "GROQ_API_KEY=your_key_here" > .env
```

Same Groq key from Project 1. Free tier — no credits needed. Get key at [console.groq.com](https://console.groq.com).
