"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform
    """
    listings = load_listings()

    # Filter by price
    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]

    # Filter by size (case-insensitive substring match)
    if size is not None:
        size_lower = size.lower()
        listings = [l for l in listings if size_lower in l["size"].lower()]

    # Score by keyword overlap with description
    keywords = description.lower().split()

    def score(listing):
        text = " ".join([
            listing["title"],
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
        ]).lower()
        return sum(1 for kw in keywords if kw in text)

    scored = [(score(l), l) for l in listings]
    # Drop zero-score listings
    scored = [(s, l) for s, l in scored if s > 0]
    # Sort highest score first
    scored.sort(key=lambda x: x[0], reverse=True)

    return [l for _, l in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.
    """
    client = _get_groq_client()
    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = (
            f"A user just found this secondhand item:\n"
            f"Item: {new_item['title']}\n"
            f"Description: {new_item['description']}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n"
            f"Colors: {', '.join(new_item['colors'])}\n\n"
            f"They don't have a wardrobe entered yet. Give them general styling advice: "
            f"what types of pieces pair well with this item, what vibe or aesthetic it suits, "
            f"and how they might build an outfit around it. Be specific and helpful. 2–3 sentences."
        )
    else:
        wardrobe_text = "\n".join(
            f"- {item['name']} ({item['category']}, colors: {', '.join(item['colors'])})"
            for item in wardrobe_items
        )
        prompt = (
            f"A user just found this secondhand item:\n"
            f"Item: {new_item['title']}\n"
            f"Description: {new_item['description']}\n"
            f"Style tags: {', '.join(new_item['style_tags'])}\n"
            f"Colors: {', '.join(new_item['colors'])}\n\n"
            f"Their wardrobe includes:\n{wardrobe_text}\n\n"
            f"Suggest 1–2 complete outfit combinations using the new item and specific pieces "
            f"from their wardrobe. Name the exact wardrobe pieces. Be specific about the look "
            f"and vibe. 3–4 sentences."
        )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)
    """
    if not outfit or not outfit.strip():
        return "Could not generate a fit card: outfit description is missing."

    client = _get_groq_client()

    prompt = (
        f"Write a 2–4 sentence Instagram caption for this thrift find. "
        f"Make it sound like a real person's OOTD post — casual, authentic, enthusiastic. "
        f"Mention the item name, price (${new_item['price']:.0f}), and platform ({new_item['platform']}) "
        f"naturally (each once). Capture the specific vibe of the outfit.\n\n"
        f"Item: {new_item['title']}\n"
        f"Outfit: {outfit}\n\n"
        f"Caption only — no hashtags, no intro like 'Here is a caption'."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()
