"""Tests for scripts/import_themealdb.py (pure functions only, no network)."""
from app.services.vocabulary import RecipeAnalysis
from scripts.import_themealdb import (
    Summary, accepted_with_tag, extract_ingredients, print_report, red_flags, scan_accepted, summarize,
)


def make_meal(meal_id, title, *pairs):
    """Build a meal dict shaped like the API: 20 slots, unused ones blank/null."""
    meal = {"idMeal": str(meal_id), "strMeal": title}
    for slot in range(1, 21):
        if slot <= len(pairs):
            meal[f"strIngredient{slot}"], meal[f"strMeasure{slot}"] = pairs[slot - 1]
        else:
            meal[f"strIngredient{slot}"] = "" if slot % 2 else None   # API uses both
            meal[f"strMeasure{slot}"] = " "
    return meal


def test_extract_ingredients_skips_blank_and_null_slots():
    meal = make_meal(1, "Toast", ("Bread", "2 slices"), ("Butter", "1 tbsp"))
    assert extract_ingredients(meal) == [("Bread", "2 slices"), ("Butter", "1 tbsp")]


def test_extract_ingredients_handles_a_meal_with_no_ingredients():
    assert extract_ingredients({"idMeal": "9", "strMeal": "Empty"}) == []


def test_summarize_counts_accepted_and_rejected():
    meals = [
        make_meal(1, "Scramble", ("Eggs", "2"), ("Milk", "1 tbsp"), ("Butter", "1 tbsp")),
        make_meal(2, "Turkey Chili", ("Turkey", "500g"), ("Kidney Beans", "1 tin")),
    ]
    summary = summarize(meals)
    assert summary.total == 2
    assert len(summary.accepted) == 1 and len(summary.rejected) == 1
    assert summary.blocks["turkey"] == 1


def test_unlocks_only_counts_recipes_blocked_by_a_single_name():
    meals = [
        make_meal(1, "A", ("Turkey", "1"), ("Onion", "1")),                    # only turkey blocks
        make_meal(2, "B", ("Turkey", "1"), ("Quinoa", "1"), ("Onion", "1")),   # turkey AND quinoa
    ]
    summary = summarize(meals)
    assert summary.blocks["turkey"] == 2
    assert summary.unlocks["turkey"] == 1     # adding turkey rescues A, not B
    assert summary.unlocks["quinoa"] == 0


def test_duplicate_meal_ids_are_counted_once():
    meal = make_meal(1, "Scramble", ("Eggs", "2"), ("Milk", "1"))
    assert summarize([meal, dict(meal)]).total == 1


def test_tag_counts_include_recipes_with_no_tags():
    meals = [
        make_meal(1, "Veg", ("Broccoli", "1"), ("Carrot", "1")),
        make_meal(2, "Ham", ("Ham", "1"), ("Bread", "1")),
    ]
    summary = summarize(meals)
    assert summary.tag_counts["vegan"] == 1
    assert summary.tag_counts["(no tags)"] == 1


def test_unknown_per_recipe_buckets_rejected_recipes():
    meals = [
        make_meal(1, "A", ("Turkey", "1"), ("Onion", "1")),                    # 1 unknown
        make_meal(2, "B", ("Turkey", "1"), ("Quinoa", "1"), ("Onion", "1")),   # 2 unknown
        make_meal(3, "C", ("Turkey", "1"), ("Quinoa", "1"), ("Tapioca", "1"), ("Fennel", "1")),  # 4 -> bucket 3
    ]
    summary = summarize(meals)
    assert summary.unknown_per_recipe[1] == 1
    assert summary.unknown_per_recipe[2] == 1
    assert summary.unknown_per_recipe[3] == 1


def test_recipe_of_only_staples_is_not_counted_as_having_unknowns():
    summary = summarize([make_meal(1, "Salty", ("Salt", "1"), ("Pepper", "1"))])
    assert len(summary.rejected) == 1
    assert sum(summary.unknown_per_recipe.values()) == 0


def test_accepted_with_tag_returns_only_recipes_that_earned_it():
    meals = [
        make_meal(1, "Veg", ("Broccoli", "1"), ("Carrot", "1")),     # all three tags
        make_meal(2, "Omelette", ("Eggs", "2"), ("Milk", "1")),      # vegetarian only
        make_meal(3, "Steak", ("Sirloin Steak", "1")),               # dairy-free only
    ]
    summary = summarize(meals)
    assert [i["meal"]["strMeal"] for i in accepted_with_tag(summary, "vegan")] == ["Veg"]
    assert len(accepted_with_tag(summary, "vegetarian")) == 2


def test_audit_prints_the_requested_tag_not_the_last_one_counted(capsys):
    # regression: the tag-count loop used to overwrite the --tag argument
    meals = [make_meal(1, "Veg", ("Broccoli", "1")), make_meal(2, "Omelette", ("Eggs", "2"))]
    print_report(summarize(meals), top=5, samples=0, tag="vegan")
    output = capsys.readouterr().out
    assert "tagged 'vegan'" in output
    assert "Veg" in output and "Omelette" not in output.split("AUDIT")[1]


# ---------- safety scan
def test_red_flags_finds_real_problems():
    assert red_flags(["Whole Milk"], ["dairy-free"]) == [("dairy-free", "milk")]
    assert ("vegetarian", "chicken") in red_flags(["Chicken Thighs"], ["vegetarian"])
    assert ("vegan", "egg") in red_flags(["Egg White"], ["vegan"])
    assert ("vegan", "honey") in red_flags(["Clear Honey"], ["vegan"])


def test_red_flags_ignores_plant_foods_that_share_a_word():
    safe = ["Coconut Milk", "Coconut Cream", "Peanut Butter", "Butternut Squash",
            "Butter Beans", "Eggplant", "Egg Plants", "Kidney Beans", "Cream of Tartar"]
    assert red_flags(safe, ["vegan", "vegetarian", "dairy-free"]) == []


def test_red_flags_for_real_recipes_from_the_audit():
    # ingredient names copied from recipes that were audited by hand and are correctly tagged
    rice_and_peas = ["Rice", "Coconut Milk", "Kidney Beans", "Water", "Kosher Salt", "Thyme", "Scotch Bonnet"]
    assert red_flags(rice_and_peas, ["vegetarian", "vegan", "dairy-free"]) == []
    cookies = ["Peanut Butter", "Sugar", "Egg"]
    assert red_flags(cookies, ["vegetarian", "dairy-free"]) == []
    slaw = ["Mayonnaise", "Lemon", "Cider Vinegar", "Wholegrain Mustard", "White Cabbage", "Carrots"]
    assert red_flags(slaw, ["vegetarian", "dairy-free"]) == []       # mayo has egg, not dairy
    assert ("vegan", "mayonnaise") in red_flags(slaw, ["vegan"])


def test_scan_accepted_reports_a_wrongly_tagged_recipe():
    # build a summary by hand with a recipe whose tag is WRONG, to prove the scan notices
    wrong = {"meal": {"strMeal": "Bad Tag"}, "pairs": [("Milk", "1 cup"), ("Flour", "1 cup")],
             "analysis": RecipeAnalysis(True, [], ["dairy-free"], ["milk", "flour"])}
    summary = Summary(total=1, accepted=[wrong])
    assert scan_accepted(summary) == [("Bad Tag", "dairy-free", "milk")]


def test_real_vocabulary_never_trips_the_scan_on_simple_recipes():
    meals = [
        make_meal(1, "Veg", ("Broccoli", "1"), ("Carrot", "1"), ("Vegetable Stock", "1 L")),
        make_meal(2, "Omelette", ("Eggs", "2"), ("Milk", "1")),
        make_meal(3, "Chicken stew", ("Chicken", "1"), ("Onion", "1"), ("Coconut Milk", "1 can")),
    ]
    assert scan_accepted(summarize(meals)) == []
