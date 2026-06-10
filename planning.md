# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
Searches the mock listings dataset for secondhand items matching a keyword description, with optional size and price filters. Returns a ranked list of matches sorted by relevance, or an empty list if nothing matches.

**Input parameters:**
- `description` (str): Keywords describing what the user is looking for (e.g., "vintage graphic tee")
- `size` (str | None): Size string to filter by, case-insensitive; None skips size filtering
- `max_price` (float | None): Maximum price inclusive; None skips price filtering

**What it returns:**
A list of matching listing dicts sorted by keyword relevance score (best first). Each dict contains: `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str | None), `platform` (str). Returns `[]` if nothing matches — never raises an exception.

**What happens if it fails or returns nothing:**
The agent sets `session["error"]` to "No listings found for '[query]'. Try broader keywords, a different size, or a higher price limit." and returns early. `suggest_outfit` is never called with empty input.

---

### Tool 2: suggest_outfit

**What it does:**
Given a thrifted item the user is considering and their current wardrobe, calls the Groq LLM to suggest 1–2 complete outfit combinations. If the wardrobe is empty, provides general styling advice for the item instead.

**Input parameters:**
- `new_item` (dict): A listing dict — the item the user is considering buying
- `wardrobe` (dict): A wardrobe dict with an `items` key containing a list of wardrobe item dicts (may be empty)

**What it returns:**
A non-empty string with outfit suggestions — either specific combinations naming pieces from the wardrobe, or general styling advice if the wardrobe is empty.

**What happens if it fails or returns nothing:**
If `wardrobe['items']` is empty, the LLM is prompted for general styling ideas (what pairs well, what vibe it suits) rather than raising an exception or returning an empty string.

---

### Tool 3: create_fit_card

**What it does:**
Given an outfit suggestion and the thrifted item, calls the Groq LLM to generate a short, casual 2–4 sentence Instagram-style caption for the find. Output must vary each run (uses higher temperature).

**Input parameters:**
- `outfit` (str): The outfit suggestion string from `suggest_outfit`
- `new_item` (dict): The listing dict for the thrifted item

**What it returns:**
A 2–4 sentence string styled like a real OOTD caption — casual, authentic, mentioning item name/price/platform naturally. Returns a descriptive error message string if `outfit` is empty or whitespace — never raises an exception.

**What happens if it fails or returns nothing:**
If `outfit` is empty or whitespace-only, returns the string "Could not generate a fit card: outfit description is missing." Does not raise an exception.

---

### Additional Tools (if any)

None.

---

## Planning Loop

**How does your agent decide which tool to call next?**

The planning loop runs in a fixed conditional sequence driven by the result of each step:

1. Parse the user query to extract `description`, `size`, and `max_price` using regex patterns.
2. Call `search_listings(description, size, max_price)`.
   - **If results == []**: set `session["error"]` with a helpful message and return early. Do not proceed.
   - **If results is non-empty**: set `session["selected_item"] = results[0]` and continue.
3. Call `suggest_outfit(session["selected_item"], session["wardrobe"])`. Store result in `session["outfit_suggestion"]`. Always continues — empty wardrobe handled inside the tool.
4. Call `create_fit_card(session["outfit_suggestion"], session["selected_item"])`. Store result in `session["fit_card"]`. Always continues — empty outfit handled inside the tool.
5. Return the session.

The agent does not loop back — it is a single-pass pipeline that branches only at step 2 when search returns nothing.

---

## State Management

**How does information from one tool get passed to the next?**

All state lives in a single session dict initialized by `_new_session(query, wardrobe)` in `agent.py`. Keys:

| Key | Set when | Used by |
|-----|----------|---------|
| `query` | init | parsing step |
| `parsed` | after query parsing | `search_listings` |
| `search_results` | after `search_listings` | selecting `selected_item` |
| `selected_item` | after selecting top result | `suggest_outfit`, `create_fit_card` |
| `wardrobe` | init | `suggest_outfit` |
| `outfit_suggestion` | after `suggest_outfit` | `create_fit_card` |
| `fit_card` | after `create_fit_card` | `app.py` output panel |
| `error` | on early exit | `app.py` error display |

No values are hardcoded between steps — each tool receives its inputs directly from session dict values populated by the previous step.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Sets `session["error"]` = "No listings found for '[query]'. Try broader keywords, a different size, or a higher price limit." Returns session early without calling further tools. |
| suggest_outfit | Wardrobe is empty (`wardrobe['items'] == []`) | Prompts LLM for general styling advice for the item. Returns a non-empty string — no exception. |
| create_fit_card | `outfit` is empty or whitespace-only | Returns string "Could not generate a fit card: outfit description is missing." — no exception. |

---

## Architecture

```
User query
    |
    v
Planning Loop (agent.py: run_agent)
    |
    |-- Step 1: parse query → session["parsed"]
    |
    |-- Step 2: search_listings(description, size, max_price)
    |               |
    |               |-- results == [] ──→ session["error"] set → return early ──┐
    |               |                                                             |
    |               └-- results non-empty → session["selected_item"] = results[0]|
    |                                                                             |
    |-- Step 3: suggest_outfit(selected_item, wardrobe)                          |
    |               |                                                             |
    |               |-- wardrobe empty → general styling advice (no crash)       |
    |               └-- wardrobe has items → specific outfit combinations        |
    |               → session["outfit_suggestion"]                               |
    |                                                                             |
    |-- Step 4: create_fit_card(outfit_suggestion, selected_item)                |
    |               |                                                             |
    |               |-- outfit empty → error string (no crash)                   |
    |               └-- outfit valid → caption string                            |
    |               → session["fit_card"]                                        |
    |                                                                             |
    └-- Return session ←──────────────────────────────────────────────────────── ┘
            |
            v
    app.py: handle_query maps session → 3 Gradio output panels
    (panel 1: listing or error | panel 2: outfit | panel 3: fit card)
```

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**

- **search_listings**: Give Claude the Tool 1 spec block (inputs, return value, failure mode) and ask it to implement the function using `load_listings()` from `utils/data_loader.py`. Verify: does it filter by both size and price? Does it return `[]` (not raise) on no match? Test with 3 queries: one that matches, one with impossible price, one with impossible size.

- **suggest_outfit**: Give Claude the Tool 2 spec block and the wardrobe schema structure (fields: id, name, category, colors, style_tags, notes). Ask it to implement using Groq `llama-3.3-70b-versatile`. Verify: does it branch on empty wardrobe? Does it return a non-empty string in both cases? Test with `get_example_wardrobe()` and `get_empty_wardrobe()`.

- **create_fit_card**: Give Claude the Tool 3 spec block. Ask it to implement with empty-outfit guard and higher temperature (0.9+). Verify: does it return an error string (not raise) on empty outfit? Run same input 3× and confirm outputs differ.

**Milestone 4 — Planning loop and state management:**

Give Claude the Planning Loop + State Management sections above plus the Architecture diagram. Ask it to implement `run_agent()` in `agent.py` following the numbered steps. Verify: does it branch on empty `search_listings` result? Does it store values in session dict between steps without re-prompting the user? Test both paths using the two test cases already in `agent.py`.

---

## A Complete Interaction (Step by Step)

FitFindr is a multi-tool AI agent that helps users find secondhand clothing and figure out how to wear it. When a user describes what they're looking for, the agent calls `search_listings` to find matches, `suggest_outfit` to build an outfit using their wardrobe, then `create_fit_card` to generate a shareable caption. If `search_listings` returns nothing, the agent tells the user what to try differently and stops — it never calls the next tool with empty input.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
Agent calls `search_listings("vintage graphic tee", size=None, max_price=30.0)`. The tool scores all listings by keyword overlap with "vintage graphic tee", filters out any priced above $30, and returns a sorted list. The Y2K Baby Tee ($18, depop) scores highest. Agent stores: `session["selected_item"] = results[0]`.

**Step 2:**
Agent calls `suggest_outfit(session["selected_item"], session["wardrobe"])`. The wardrobe has baggy jeans (w_001), chunky white sneakers (w_007), and other pieces. LLM returns specific outfit combinations naming those pieces. Agent stores result in `session["outfit_suggestion"]`.

**Step 3:**
Agent calls `create_fit_card(session["outfit_suggestion"], session["selected_item"])`. LLM generates a casual 2–4 sentence caption mentioning the item name, $18 price, and depop. Agent stores in `session["fit_card"]`.

**Final output to user:**
Three panels in the Gradio UI: (1) listing details for the Y2K Baby Tee, (2) the outfit suggestion, (3) the shareable fit card caption.

**Error path:**
If Step 1 returns `[]` (e.g., "designer ballgown size XXS under $5"), agent sets `session["error"]` = "No listings found for 'designer ballgown'. Try broader keywords, a different size, or a higher price limit." and returns. Steps 2 and 3 never run. UI shows the error in panel 1, panels 2 and 3 are empty.
