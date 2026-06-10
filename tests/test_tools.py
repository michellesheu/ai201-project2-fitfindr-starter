"""
tests/test_tools.py

Tests for each FitFindr tool. Covers the happy path and at least one
failure mode per tool. Run with: pytest tests/
"""

import pytest
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


# ── search_listings ───────────────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    # Impossible query — should return [] not raise
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


def test_search_size_filter():
    results = search_listings("shirt", size="XL", max_price=None)
    assert all("xl" in item["size"].lower() for item in results)


def test_search_returns_list_of_dicts():
    results = search_listings("jeans", size=None, max_price=100)
    if results:
        assert "id" in results[0]
        assert "title" in results[0]
        assert "price" in results[0]


def test_search_no_price_filter():
    # No filters — should return all matches
    all_results = search_listings("vintage", size=None, max_price=None)
    assert len(all_results) > 0


# ── suggest_outfit ────────────────────────────────────────────────────────────

def test_suggest_outfit_with_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert results, "Need at least one result to test suggest_outfit"
    item = results[0]
    suggestion = suggest_outfit(item, get_example_wardrobe())
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0


def test_suggest_outfit_empty_wardrobe():
    # Failure mode: empty wardrobe should return labeled general advice, not crash
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert results
    item = results[0]
    suggestion = suggest_outfit(item, get_empty_wardrobe())
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0
    # Must self-identify as general advice (not look like a normal outfit suggestion)
    assert "general styling advice" in suggestion.lower() or "haven't added" in suggestion.lower()


# ── create_fit_card ───────────────────────────────────────────────────────────

def test_create_fit_card_returns_caption():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert results
    item = results[0]
    outfit = "Pair this tee with baggy jeans and chunky sneakers for a classic 90s look."
    card = create_fit_card(outfit, item)
    assert isinstance(card, str)
    assert len(card) > 0


def test_create_fit_card_empty_outfit():
    # Failure mode: empty outfit should return error string, not raise
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert results
    item = results[0]
    card = create_fit_card("", item)
    assert isinstance(card, str)
    assert "missing" in card.lower() or "could not" in card.lower()


def test_create_fit_card_whitespace_outfit():
    # Whitespace-only outfit should also return error string
    results = search_listings("jacket", size=None, max_price=100)
    assert results
    item = results[0]
    card = create_fit_card("   ", item)
    assert isinstance(card, str)
    assert len(card) > 0
    assert "missing" in card.lower() or "could not" in card.lower()
