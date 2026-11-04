"""What GET /recipes/match says about each result. """
from app.models.models import Ingredient, Recipe, User


def build_kitchen(db):
    """Four ingredients and three recipes with a known overlap. Returns {ingredient name: id}."""
    owner = User(email="owner@example.com", hashed_password="not-a-real-hash")
    ingredients = {name: Ingredient(name=name) for name in ("egg", "milk", "butter", "ham")}
    db.add_all([owner, *ingredients.values()])
    db.flush()

    def recipe(title, *names):
        db.add(Recipe(title=title, instructions="Cook.", owner_id=owner.id,
                      ingredients=[ingredients[n] for n in names]))

    recipe("Scramble", "egg", "milk", "butter")
    recipe("Omelette", "egg", "milk", "butter", "ham")
    recipe("Toast", "butter")
    db.commit()
    return {name: item.id for name, item in ingredients.items()}


def match(client, ids, *names):
    query = "&".join(f"ingredient_ids={ids[name]}" for name in names)
    response = client.get(f"/recipes/match?{query}")
    assert response.status_code == 200
    return response.json()


def test_match_score_is_matched_divided_by_total(client, db):
    ids = build_kitchen(db)
    results = {r["title"]: r for r in match(client, ids, "egg", "milk", "butter")}
    assert results["Scramble"]["match_score"] == 1.0     # has 3 of 3
    assert results["Omelette"]["match_score"] == 0.75    # has 3 of 4
    assert results["Toast"]["match_score"] == 1.0        # has 1 of 1


def test_results_are_ranked_by_coverage_then_fewest_missing_then_most_matched(client, db):
    ids = build_kitchen(db)
    titles = [r["title"] for r in match(client, ids, "egg", "milk", "butter")]
    # Scramble and Toast both cover 100% with nothing missing; Scramble matched more.
    assert titles == ["Scramble", "Toast", "Omelette"]


def test_each_result_says_what_is_matched_and_what_is_missing(client, db):
    ids = build_kitchen(db)
    omelette = next(r for r in match(client, ids, "egg", "milk", "butter") if r["title"] == "Omelette")
    assert omelette["matched_count"] == 3 and omelette["total_ingredients"] == 4
    assert [m["name"] for m in omelette["missing_ingredients"]] == ["ham"]