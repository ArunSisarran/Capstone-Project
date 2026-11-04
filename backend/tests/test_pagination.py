"""Limits and ordering on the list and match endpoints"""
from sqlalchemy import event

from app.models.models import Ingredient, Recipe, User


def add_recipes(db, count):
    """An owner, one ingredient, and `count` recipes that all use it."""
    owner = User(email="owner@example.com", hashed_password="not-a-real-hash")
    egg = Ingredient(name="egg")
    db.add_all([owner, egg])
    db.flush()
    db.add_all(
        Recipe(title=f"Recipe {n}", instructions="Cook.", owner_id=owner.id, ingredients=[egg])
        for n in range(1, count + 1)
    )
    db.commit()
    return egg.id


# ---------- GET /recipes
def test_limit_must_be_between_1_and_100(client):
    for bad in (0, -1, 101, 100000):
        assert client.get(f"/recipes?limit={bad}").status_code == 422, bad
    for good in (1, 100):
        assert client.get(f"/recipes?limit={good}").status_code == 200, good


def test_skip_cannot_be_negative(client):
    assert client.get("/recipes?skip=-1").status_code == 422
    assert client.get("/recipes?skip=0").status_code == 200


def test_filter_ids_must_be_real_database_ids(client):
    for bad in ("0", "-3", "99999999999"):
        assert client.get(f"/recipes?ingredient_id={bad}").status_code == 422, bad
        assert client.get(f"/recipes?dietary_tag_id={bad}").status_code == 422, bad


def test_pages_do_not_repeat_or_skip_recipes(client, db):
    add_recipes(db, 5)
    seen = []
    for skip in (0, 2, 4):
        seen += [r["id"] for r in client.get(f"/recipes?limit=2&skip={skip}").json()]
    assert seen == [1, 2, 3, 4, 5]


def test_the_list_query_is_ordered_by_id(client, db, engine):
    # Without ORDER BY the database may return rows in any order, so pages can overlap.
    # SQLite happens to use id order anyway, so check the SQL itself.
    add_recipes(db, 3)
    statements = []
    event.listen(engine, "before_cursor_execute",
                 lambda conn, cursor, statement, *rest: statements.append(statement))
    client.get("/recipes?limit=2")
    assert any("ORDER BY recipes.id" in s for s in statements)


# ---------- GET /recipes/match
def test_match_needs_at_least_one_ingredient_id(client):
    assert client.get("/recipes/match").status_code == 422


def test_match_rejects_ids_that_cannot_exist(client):
    for bad in ("0", "-1", "99999999999"):
        assert client.get(f"/recipes/match?ingredient_ids={bad}").status_code == 422, bad


def test_match_rejects_too_many_ids(client):
    many = "&".join(f"ingredient_ids={i}" for i in range(1, 52))
    assert client.get(f"/recipes/match?{many}").status_code == 422
    fifty = "&".join(f"ingredient_ids={i}" for i in range(1, 51))
    assert client.get(f"/recipes/match?{fifty}").status_code == 200


def test_match_limit_and_skip_are_bounded(client):
    for bad in ("limit=0", "limit=101", "skip=-1"):
        assert client.get(f"/recipes/match?ingredient_ids=1&{bad}").status_code == 422, bad


def test_match_still_returns_results(client, db):
    egg_id = add_recipes(db, 3)
    results = client.get(f"/recipes/match?ingredient_ids={egg_id}").json()
    assert [r["title"] for r in results] == ["Recipe 1", "Recipe 2", "Recipe 3"]