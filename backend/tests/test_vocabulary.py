"""Tests for app/services/vocabulary.py. Run from backend/:  python -m pytest"""
import csv

import pytest

from app.services.vocabulary import (
    VOCAB_FILE, analyze_recipe, all_canonical_names, canonical_names, derive_tags, load_table, normalize, resolve,
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
    # aliases added after the first real TheMealDB report (some are typos in the source data)
    ("tinned tomatos", "Tomato"),
    ("Challots", "Onion"),
    ("egg plants", "Eggplant"),
    ("melted butter", "Butter"),
    ("flaked almonds", "Nuts"),
    ("raw king prawns", "Shrimp"),
    ("coriander leaves", "Herbs"),
    ("clear honey", "Honey"),
    ("sirloin steak", "Meat"),
    ("paella rice", "Rice"),
    # round 2, from the full 790-recipe report
    ("sesame seed oil", "Oil"),
    ("Scotch Bonnet", "Chili"),
    ("muscovado sugar", "Sugar"),
    ("cheddar cheese", "Cheese"),
    ("ground pork", "Meat"),
    ("marjoram", "Herbs"),
    # round 3
    ("lamb leg", "Meat"),
    ("Pistachio", "Nuts"),
    ("strong white bread flour", "Flour"),
    ("ground nut oil", "Oil"),
    ("vanilla sugar", "Sugar"),
    ("dried white beans", "Beans"),
    ("salt cod", "Fish"),
    # round 4
    ("minced garlic", "Garlic"),
    ("russet potato", "Potato"),
    ("crusty bread", "Bread"),
    ("dark brown soft sugar", "Sugar"),
    ("lemongrass stalks", "Herbs"),
])
def test_resolve_maps_to_expected_class(raw, canonical):
    assert resolve(raw).canonical == canonical


def test_plain_pepper_is_the_black_pepper_staple():
    assert resolve("pepper").is_staple


@pytest.mark.parametrize("raw", [
    "cinnamon stick", "caraway seed", "corn flour", "almond extract",
    "ground nutmeg", "sherry vinegar", "dry white wine", "thai red curry paste",
    "golden syrup", "sesame seed", "ground cardomom", "dried mint", "starch",
])
def test_newly_added_staples_are_staples(raw):
    assert resolve(raw).is_staple


@pytest.mark.parametrize("raw", ["puff pastry", "condensed milk", "fennel", "rice noodles", "dulce de leche"])
def test_deliberately_unsupported_ingredients_stay_unknown(raw):
    # pastry/condensed milk are key ingredients, not invisible pantry staples
    assert resolve(raw) is None


@pytest.mark.parametrize("raw", ["turkey", "quinoa", "clove", "", "   "])
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


def test_curry_paste_and_wine_block_vegetarian_but_not_dairy_free():
    # both may hide animal products (shrimp paste, fining agents), so 'unsure'
    for ingredient in ("thai red curry paste", "dry white wine"):
        assert analyze_recipe(["onion", ingredient]).tags == ["dairy-free"]


def test_syrups_do_not_block_any_tag():
    assert analyze_recipe(["flour", "golden syrup"]).tags == ["vegetarian", "vegan", "dairy-free"]


def test_liquid_vegetable_stock_is_vegan_but_stock_cubes_are_not_assumed_to_be():
    # found while auditing the vegan list: cubes/powders can contain milk or whey
    assert analyze_recipe(["carrot", "vegetable stock"]).tags == ["vegetarian", "vegan", "dairy-free"]
    assert analyze_recipe(["carrot", "vegetable stock cube"]).tags == ["vegetarian"]

def test_all_canonical_names_are_the_detectable_classes_only():
    names = all_canonical_names()
    assert "bell pepper" in names and "dragon fruit" in names
    assert "salt" not in names and "oil" not in names        # ignored for matching
    assert not any(name in names for name in ("black pepper", "water", "spices"))  # staples
    assert names == sorted(set(names)) and all(name == name.lower() for name in names)
    assert len(names) >= 80