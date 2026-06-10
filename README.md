# FitFindr

A multi-tool AI agent that helps users find secondhand clothing and figure out how to wear it. Given a natural language query, FitFindr searches a mock thrift listings dataset, suggests outfit combinations using the user's wardrobe, and generates a shareable caption for the find.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root (never commit this):
```
GROQ_API_KEY=your_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

## Running the App

```bash
python app.py
```

Open the URL shown in your terminal (check output — may not be `localhost:7860`).

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Tool Inventory

### `search_listings(description, size, max_price)`

**Purpose:** Searches the mock listings dataset for secondhand items matching a keyword description with optional size and price filters.

**Inputs:**
- `description` (str) — keywords describing what the user is looking for (e.g., "vintage graphic tee")
- `size` (str | None) — size string to filter by, case-insensitive substring match; `None` skips size filtering
- `max_price` (float | None) — maximum price inclusive; `None` skips price filtering

**Output:** `list[dict]` — matching listing dicts sorted by keyword relevance score (best first), or `[]` if nothing matches. Each dict has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`.

---

### `suggest_outfit(new_item, wardrobe)`

**Purpose:** Given a thrifted item and the user's wardrobe, suggests 1–2 complete outfit combinations using the Groq LLM.

**Inputs:**
- `new_item` (dict) — a listing dict for the item the user is considering
- `wardrobe` (dict) — wardrobe dict with an `items` key (list of wardrobe item dicts, may be empty)

**Output:** `str` — non-empty outfit suggestion string. If the wardrobe is empty, returns general styling advice for the item instead of outfit combinations.

---

### `create_fit_card(outfit, new_item)`

**Purpose:** Generates a short, shareable Instagram-style caption for the thrift find.

**Inputs:**
- `outfit` (str) — outfit suggestion from `suggest_outfit`
- `new_item` (dict) — listing dict for the thrifted item

**Output:** `str` — 2–4 sentence casual caption mentioning item name, price, and platform. If `outfit` is empty, returns `"Could not generate a fit card: outfit description is missing."` — no exception.

---

## How the Planning Loop Works

The planning loop in `agent.py` runs as a conditional single-pass pipeline:

1. **Parse** the user's query with regex to extract `description`, `size`, and `max_price`.
2. **Search** — call `search_listings`. **If results are empty, set `session["error"]` and return immediately.** `suggest_outfit` is never called with empty input.
3. **Outfit** — call `suggest_outfit` with the top result and the user's wardrobe. Always continues (empty wardrobe handled inside the tool).
4. **Fit card** — call `create_fit_card` with the outfit suggestion and selected item. Always continues (empty outfit handled inside the tool).
5. **Return** the session dict.

The agent responds differently to different inputs — the only branch is at step 2 based on what `search_listings` returns.

---

## State Management

All state is stored in a single session dict initialized at the start of each `run_agent()` call. Tool outputs are written into the session, and subsequent tools read directly from it — no values are hardcoded or re-entered between steps.

| Key | When set | Consumed by |
|-----|----------|-------------|
| `query` | init | query parser |
| `parsed` | after parsing | `search_listings` |
| `search_results` | after `search_listings` | item selection |
| `selected_item` | after item selection | `suggest_outfit`, `create_fit_card` |
| `wardrobe` | init | `suggest_outfit` |
| `outfit_suggestion` | after `suggest_outfit` | `create_fit_card` |
| `fit_card` | after `create_fit_card` | `app.py` output panel 3 |
| `error` | on early exit | `app.py` output panel 1 |

**State passing in practice:** After `search_listings` returns, `session["selected_item"]` is set to `results[0]`. That exact dict is passed into `suggest_outfit` — not re-fetched, not re-described. The outfit string returned by `suggest_outfit` is stored in `session["outfit_suggestion"]` and passed directly into `create_fit_card`.

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No listings match the query | Returns `[]`. Agent sets `session["error"]` = `"No listings found for '[description]'. Try broader keywords, a different size, or a higher price limit."` and returns early. Subsequent tools not called. |
| `suggest_outfit` | Wardrobe is empty | Detected by checking `wardrobe['items'] == []`. Prompts the LLM for general styling advice instead of outfit combinations. Always returns a non-empty string. **Tested:** `suggest_outfit(item, get_empty_wardrobe())` returns general pairing advice without crashing. |
| `create_fit_card` | Outfit string is empty or whitespace | Guard at top of function: `if not outfit or not outfit.strip()`. Returns `"Could not generate a fit card: outfit description is missing."` — no LLM call, no exception. **Tested:** `create_fit_card("", item)` returns the error string. |

---

## Spec Reflection

**One way the spec helped:** Writing the planning loop section of `planning.md` with explicit conditional logic ("if results == [], set error and return early") made the implementation straightforward — the spec was specific enough that the code was almost a direct translation. Without that detail, the LLM-assisted implementation would have produced a loop that called all three tools unconditionally.

**One way implementation diverged from spec:** The query parser in the spec was described vaguely as "regex patterns." In practice, extracting size correctly required multiple regex alternatives (matching "size M", "in M", standalone "M") and some filler phrase removal. The final parser handles the common cases well but would miss edge cases like "W30 waist" or numeric sizes — something worth noting for future improvement.

---

## AI Usage

**Instance 1 — search_listings implementation:**
I gave Claude Code the Tool 1 spec from `planning.md` (inputs, return value, failure mode) and asked it to implement `search_listings` using `load_listings()` from `utils/data_loader.py`. It produced a keyword-scoring function that scored listings by counting keyword matches across title, description, category, and style_tags. Before using it, I verified that it: (a) filters by both size and price before scoring, (b) returns `[]` rather than raising when no match, and (c) drops zero-score listings. I then confirmed with `pytest tests/` that all six `search_listings` tests passed.

**Instance 2 — planning loop and agent diagram:**
I gave Claude Code the Planning Loop, State Management, and Architecture sections from `planning.md` (including the ASCII diagram) and asked it to implement `run_agent()` in `agent.py`. The generated code matched the spec's conditional structure. I reviewed it for: does it branch on empty search results? does it store values into session dict without re-prompting? I then tested both paths from the CLI (`python agent.py`) and confirmed the no-results path sets `session["error"]` and leaves `session["fit_card"]` as `None`.
