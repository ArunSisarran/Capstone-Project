"""Tests for app/services/vocabulary.py. Run from backend/:  python -m pytest"""
import csv

import pytest

from app.services.vocabulary import (
    VOCAB_FILE, analyze_recipe, canonical_names, derive_tags, load_table, normalize, resolve,
)


# ---------- normalize
def test_normalize_trims_lowercases_and_drops_punctuation():
    assert normalize("  Chicken Breasts, ") == "chicken breasts"


def test_normalize_strips_accents_and_hyphens():
    assert normalize("Crème Fraîche") == "creme fraiche"
    assert normalize("Free-Range Eggs") == "free range eggs"
    assert normalize("Za'atar") == "zaatar"


# ---------- table loading / data integrity
def test_table_loads_without_conflicts_or_bad_flags():
    # load_table raises ValueError on duplicate aliases or bad yes/no/unsure
    assert len(load_table()) > 500


def test_every_canonical_class_resolves_to_itself():
    # The recognition endpoint passes the model's class names straight to
    # resolve(), so every canonical name must also work as an alias.
    with open(VOCAB_FILE, newline="", encoding="utf-8") as handle:
        names = {row["canonical"] for row in csv.DictReader(handle)}
    for name in names:
        assert resolve(name).canonical == name


# ---------- resolve: the traps
@pytest.mark.parametrize("raw, canonical", [
    ("Chicken Breasts", "Chicken"),
    ("tomatoes", "Tomato"),              # plural fallback ("es")
    ("Brussels Sprouts", "Cabbage"),
    ("peanut butter", "Nuts"),           # not Butter
    ("coconut milk", "Coconut"),         # not Milk
    ("Eggplant", "Eggplant"),            # not Egg
    ("red pepper", "Bell Pepper"),
    ("Crème Fraîche", "Cream"),
])
def test_resolve_maps_to_expected_class(raw, canonical):
    assert resolve(raw).canonical == canonical


def test_plain_pepper_is_the_black_pepper_staple():
    assert resolve("pepper").is_staple


@pytest.mark.parametrize("raw", ["turkey", "molasses", "clove", "", "   "])
def test_unknown_names_return_none(raw):
    assert resolve(raw) is None


# ---------- derive_tags / canonical_names
def test_empty_recipe_gets_no_tags():
    assert derive_tags([]) == []


def test_salt_and_oil_are_not_matched_on():
    assert canonical_names([resolve("salt"), resolve("olive oil"), resolve("onion")]) == ["onion"]


# ---------- whole recipes
def test_vegetable_stir_fry_gets_all_three_tags():
    result = analyze_recipe(["broccoli", "carrot", "soy sauce", "oil", "garlic", "water"])
    assert result.accepted
    assert result.tags == ["vegetarian", "vegan", "dairy-free"]
    assert result.canonical == ["broccoli", "carrot", "garlic"]


def test_coconut_curry_is_fully_plant_based():
    result = analyze_recipe(["coconut milk", "onion", "chickpeas", "curry powder", "rice"])
    assert result.tags == ["vegetarian", "vegan", "dairy-free"]
    assert result.canonical == ["beans", "coconut", "onion", "rice"]


def test_omelette_gets_no_tags_but_is_accepted():
    result = analyze_recipe(["eggs", "milk", "butter", "ham", "salt", "pepper"])
    assert result.accepted and result.tags == []
    assert result.canonical == ["butter", "egg", "ham", "milk"]


def test_peanut_butter_toast_is_only_vegetarian():
    # bread is 'unsure' for vegan and dairy-free; honey is not vegan
    result = analyze_recipe(["bread", "peanut butter", "honey"])
    assert result.tags == ["vegetarian"]


def test_eggplant_bake_is_vegetarian_only():
    result = analyze_recipe(["eggplant", "tomato paste", "cheese", "herbs"])
    assert result.tags == ["vegetarian"]


def test_worcestershire_sauce_blocks_vegetarian():
    result = analyze_recipe(["lettuce", "chicken breast", "parmesan", "worcestershire sauce"])
    assert result.accepted and result.tags == []
    # and on its own, a staple that hides anchovies must remove the tag
    assert "vegetarian" not in analyze_recipe(["lettuce", "worcestershire sauce"]).tags



def test_generic_sauce_blocks_every_tag():
    result = analyze_recipe(["pasta", "sauce", "onion"])
    assert result.accepted and result.tags == []


def test_unknown_ingredient_rejects_the_recipe():
    result = analyze_recipe(["turkey", "kidney beans", "chili powder"])
    assert not result.accepted
    assert result.unknown == ["turkey"]
    assert result.tags == [] and result.canonical == []


def test_recipe_of_only_staples_is_rejected():
    assert not analyze_recipe(["water", "pepper", "salt"]).accepted    