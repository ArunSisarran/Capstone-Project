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


def test_ingredient_ids_are_required(client):
    assert client.get("/recipes/match").status_code == 422


def test_more_than_50_ingredient_ids_is_rejected(client):
    query = "&".join(f"ingredient_ids={i}" for i in range(1, 52))
    assert client.get(f"/recipes/match?{query}").status_code == 422


def test_ids_that_match_no_recipe_return_an_empty_list(client, db):
    build_kitchen(db)
    response = client.get("/recipes/match?ingredient_ids=9999")
    assert response.status_code == 200
    assert response.json() == []


def test_recipes_with_no_matching_ingredient_are_left_out(client, db):
    ids = build_kitchen(db)
    # only Omelette contains ham, so it is the only result (a weak 1 of 4 match)
    assert [r["title"] for r in match(client, ids, "ham")] == ["Omelette"]


def test_duplicate_ids_do_not_double_count(client, db):
    ids = build_kitchen(db)
    once = match(client, ids, "egg", "milk", "butter")
    twice = match(client, ids, "egg", "egg", "milk", "milk", "butter")
    assert once == twice


def test_limit_must_be_between_1_and_100(client, db):
    ids = build_kitchen(db)
    for bad_limit in (0, 101):
        response = client.get(f"/recipes/match?ingredient_ids={ids['egg']}&limit={bad_limit}")
        assert response.status_code == 422


def test_skip_and_limit_page_through_results_without_repeats(client, db):
    ids = build_kitchen(db)
    query = "&".join(f"ingredient_ids={ids[name]}" for name in ("egg", "milk", "butter"))
    everything = [r["title"] for r in client.get(f"/recipes/match?{query}").json()]
    first = [r["title"] for r in client.get(f"/recipes/match?{query}&limit=2").json()]
    second = [r["title"] for r in client.get(f"/recipes/match?{query}&skip=2&limit=2").json()]
    assert first + second == everything
    assert len(everything) == 3


def test_ingredient_ids_are_required(client):
    assert client.get("/recipes/match").status_code == 422


def test_more_than_50_ingredient_ids_is_rejected(client):
    query = "&".join(f"ingredient_ids={i}" for i in range(1, 52))
    assert client.get(f"/recipes/match?{query}").status_code == 422


def test_ids_that_match_no_recipe_return_an_empty_list(client, db):
    build_kitchen(db)
    response = client.get("/recipes/match?ingredient_ids=9999")
    assert response.status_code == 200
    assert response.json() == []


def test_recipes_with_no_matching_ingredient_are_left_out(client, db):
    ids = build_kitchen(db)
    # only Omelette contains ham, so it is the only result (a weak 1 of 4 match)
    assert [r["title"] for r in match(client, ids, "ham")] == ["Omelette"]


def test_duplicate_ids_do_not_double_count(client, db):
    ids = build_kitchen(db)
    once = match(client, ids, "egg", "milk", "butter")
    twice = match(client, ids, "egg", "egg", "milk", "milk", "butter")
    assert once == twice


def test_limit_must_be_between_1_and_100(client, db):
    ids = build_kitchen(db)
    for bad_limit in (0, 101):
        response = client.get(f"/recipes/match?ingredient_ids={ids['egg']}&limit={bad_limit}")
        assert response.status_code == 422


def test_skip_and_limit_page_through_results_without_repeats(client, db):
    ids = build_kitchen(db)
    query = "&".join(f"ingredient_ids={ids[name]}" for name in ("egg", "milk", "butter"))
    everything = [r["title"] for r in client.get(f"/recipes/match?{query}").json()]
    first = [r["title"] for r in client.get(f"/recipes/match?{query}&limit=2").json()]
    second = [r["title"] for r in client.get(f"/recipes/match?{query}&skip=2&limit=2").json()]
    assert first + second == everything
    assert len(everything) == 3
