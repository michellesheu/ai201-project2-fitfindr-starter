# FitFindr Demo Script (~3 minutes)

---

## [0:00–0:25] Intro

**Show:** App running at localhost, FitFindr title screen, query box + 3 empty output panels.

> "Hi, this is FitFindr — a multi-tool AI agent for thrift shopping. The user gives a natural language query, and the agent orchestrates three tools: it searches secondhand listings, suggests an outfit using the user's wardrobe, then generates a shareable caption. I'll walk through a complete interaction, then show how it handles failure. The key thing to watch is how state passes from one tool to the next — no value gets re-entered between steps."

---

## [0:25–1:45] Happy path — all 3 tools in sequence

**Show:** Type `vintage graphic tee under $30` with **"Example wardrobe"** selected. Click "Find it."

> "I'm searching for a vintage graphic tee under $30 against the example wardrobe. When I submit, the planning loop kicks off."

**Show:** Point to **Panel 1** (listing) as it fills.

> "Step 1 — `search_listings`. The agent parsed my query into a description, no size, and a max price of $30. It scored every listing by keyword overlap and filtered by price. The top match is the Y2K Baby Tee — $18 on Depop. That listing dict is now stored in the session as `selected_item`."

**Show:** Point to **Panel 2** (outfit).

> "Step 2 — `suggest_outfit`. Here's the state passing: that exact `selected_item` dict was handed to the next tool, along with my wardrobe — the agent didn't re-ask what's in my closet. Notice the suggestion names my specific pieces: baggy straight-leg jeans, chunky white sneakers. It pulled those straight from session state."

**Show:** Point to **Panel 3** (fit card).

> "Step 3 — `create_fit_card`. The outfit text from step 2 becomes the input here. The agent generates a casual caption that names the item, the $18 price, and Depop — ready to post. That's the full pipeline: query → search → outfit → fit card, with each tool's output feeding the next."

---

## [1:45–2:30] Visible failure — no-results path

**Show:** Clear the query box. Type `designer ballgown size XXS under $5`. Click "Find it."

> "Now let's deliberately break it. There's no designer ballgown in size XXS under $5 in the dataset — `search_listings` will return nothing."

**Show:** Panel 1 shows the error message; panels 2 and 3 are empty.

> "Here's the graceful failure. `search_listings` returned an empty list — no exception, no crash. The planning loop detected that and returned early: it set an informative error message and did *not* call `suggest_outfit` or `create_fit_card` with empty input. The user gets actionable guidance — try broader keywords, a different size, or a higher price limit — instead of a blank screen or a stack trace."

---

## [2:30–3:00] Robustness highlight — empty wardrobe

**Show:** Reset to `vintage graphic tee under $30`, switch to **"Empty wardrobe (new user)"**. Click "Find it."

> "One more robustness highlight. This user hasn't entered any wardrobe items yet. Watch panel 2."

**Show:** Panel 2 shows the labeled general advice.

> "`suggest_outfit` detected the empty wardrobe and clearly told the user — 'You haven't added any wardrobe items yet — here's some general styling advice for this piece' — then gave useful guidance anyway. No crash, no empty string, and it's immediately clear why the response looks different from a normal outfit suggestion."

---

## [3:00] Close

> "So FitFindr responds differently based on what each tool returns — it's not a fixed sequence. State flows through a single session dict, every tool handles its own failure mode, and the agent communicates clearly when something doesn't go as planned. That's FitFindr."

---

## Recording notes

- Pre-type all three queries so you don't fumble.
- LLM calls take 2–4 seconds — pause narration or trim dead air in editing.
- Total runtime with pauses: ~3 min. Trim the intro if running long.
