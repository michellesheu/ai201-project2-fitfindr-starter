"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Usage:
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import re

from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


def _parse_query(query: str) -> dict:
    """
    Extract description, size, and max_price from a natural language query.

    Returns a dict with keys: description (str), size (str|None), max_price (float|None).
    """
    # Extract price: "under $30", "$30", "30 dollars", "max $30"
    price_match = re.search(r'(?:under|max|below|up to)?\s*\$?(\d+(?:\.\d+)?)\s*(?:dollars?)?', query, re.IGNORECASE)
    max_price = float(price_match.group(1)) if price_match else None

    # Extract size: "size M", "size XL", "in M", standalone size tokens
    size_match = re.search(
        r'\bsize\s+([A-Z]{1,3}(?:/[A-Z]{1,3})?|\d+(?:\s*[xX]\s*\d+)?)\b'
        r'|\bin\s+(XS|S|M|L|XL|XXL|XXXL)\b'
        r'|\b(XS|S|M|L|XL|XXL|XXXL)\b',
        query, re.IGNORECASE
    )
    size = None
    if size_match:
        size = next(g for g in size_match.groups() if g is not None).upper()

    # Description: strip price/size tokens, clean up
    description = query
    if price_match:
        description = description[:price_match.start()].strip() + " " + description[price_match.end():].strip()
    if size_match:
        description = description[:size_match.start()].strip() + " " + description[size_match.end():].strip()
    # Strip filler phrases
    for phrase in ["i'm looking for", "looking for", "i want", "find me", "i need", "under", "in a", "in"]:
        description = re.sub(rf'\b{re.escape(phrase)}\b', '', description, flags=re.IGNORECASE)
    description = re.sub(r'\s+', ' ', description).strip()

    return {"description": description, "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.
    """
    # Step 1: Initialize session
    session = _new_session(query, wardrobe)

    # Step 2: Parse query
    session["parsed"] = _parse_query(query)
    parsed = session["parsed"]

    # Step 3: Search listings — branch on empty results
    session["search_results"] = search_listings(
        description=parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )

    if not session["search_results"]:
        session["error"] = (
            f"No listings found for '{parsed['description']}'. "
            f"Try broader keywords, a different size, or a higher price limit."
        )
        return session

    # Step 4: Select top result
    session["selected_item"] = session["search_results"][0]

    # Step 5: Suggest outfit
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=session["wardrobe"],
    )

    # Step 6: Create fit card
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"],
    )

    # Step 7: Return session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
    print(f"fit_card is None: {session2['fit_card'] is None}")
