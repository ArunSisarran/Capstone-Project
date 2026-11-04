"""Tests for scripts/seed_database.py.

The database tests use an in-memory SQLite database. DATABASE_URL is forced to
sqlite BEFORE any `app` import, so the real database can never be reached.
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("SECRET_KEY", "test-secret-not-used-for-anything-real")

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.security import verify_password
from app.models.models import DietaryTag, Recipe, Ingredient, User
from app.services.vocabulary import all_canonical_names
from scripts.import_themealdb import Summary, commit_to_database, summarize
from scripts.seed_database import (
    FALLBACK_SOURCE_URL, SEED_EMAIL, build_instructions, build_source_url,
    get_or_create_ingredients, get_or_create_seed_user, get_or_create_tags,
    plan_inserts, seed,
)


@pytest.fixture()
def factory():
    """Makes sessions on one shared in-memory database (a new, empty one per test)."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture()
def session(factory):
    db = factory()
    yield db
    db.close()
    db.close()
def test_source_url_prefers_the_recipes_own_page_else_the_fallback():
    assert build_source_url({"idMeal": "1", "strSource": " https://x.com/r "}) == "https://x.com/r"
    assert build_source_url({"idMeal": "52", "strSource": ""}) == FALLBACK_SOURCE_URL.format(meal_id="52")
    assert build_source_url({"idMeal": "7"}) == FALLBACK_SOURCE_URL.format(meal_id="7")


def test_instructions_keep_original_ingredient_lines_normalise_newlines_and_credit_the_source():
    meal = {"strInstructions": "Cook it.\r\nServe."}
    text = build_instructions(meal, [("Bread", "2 slices"), ("Butter", "")])
    assert text.startswith("Ingredients:\n- 2 slices Bread\n- Butter\n\nInstructions:\n")
    assert "Cook it.\nServe." in text and "\r" not in text
    assert text.endswith("TheMealDB (https://www.themealdb.com)")


def test_a_recipe_without_instructions_gets_a_placeholder():
    assert "(No instructions provided.)" in build_instructions({}, [("Bread", "")])
    assert "(No instructions provided.)" in build_instructions({"strInstructions": "  \r\n "}, [("Bread", "")])

# ---------- get-or-create: the seed user
def test_the_seed_user_is_created_once(session):
    user, created = get_or_create_seed_user(session)
    session.commit()
    again, created_again = get_or_create_seed_user(session)
    assert created and not created_again
    assert again.id == user.id and user.email == SEED_EMAIL
    assert len(session.scalars(select(User)).all()) == 1


def test_the_seed_user_has_an_unguessable_password(session):
    user, _ = get_or_create_seed_user(session)
    assert user.hashed_password and not verify_password("password", user.hashed_password)


# ---------- get-or-create: the dietary tags
def test_the_three_dietary_tags_are_created_once(session):
    tags, created = get_or_create_tags(session)
    session.commit()
    assert set(tags) == {"vegetarian", "vegan", "dairy-free"} and created == 3
    _, created_again = get_or_create_tags(session)
    assert created_again == 0 and len(session.scalars(select(DietaryTag)).all()) == 3


def test_existing_dietary_tags_are_reused_even_when_capitalised_differently(session):
    session.add(DietaryTag(name="Vegan"))
    session.commit()
    tags, created = get_or_create_tags(session)
    assert created == 2 and tags["vegan"].name == "Vegan"
    assert len(session.scalars(select(DietaryTag)).all()) == 3


# ---------- get-or-create: the ingredient rows
def test_every_detectable_class_becomes_an_ingredient_row(session):
    names = all_canonical_names()
    rows, created = get_or_create_ingredients(session, names)
    session.commit()
    assert created == len(names) and set(rows) == set(names)
    assert {row.name for row in session.scalars(select(Ingredient))} == set(names)


def test_existing_ingredient_rows_are_reused_even_when_capitalised_differently(session):
    session.add(Ingredient(name="Tomato"))
    session.commit()
    rows, created = get_or_create_ingredients(session, ["tomato", "onion"])
    session.commit()
    assert created == 1                          # only "onion" is new
    assert rows["tomato"].name == "Tomato"       # the original row, not a second "tomato"
    assert sorted(row.name for row in session.scalars(select(Ingredient))) == ["Tomato", "onion"]


def test_running_the_ingredient_step_twice_creates_nothing_the_second_time(session):
    names = all_canonical_names()
    get_or_create_ingredients(session, names)
    session.commit()
    _, created_again = get_or_create_ingredients(session, names)
    assert created_again == 0    

# ---------- planning and seeding
def make_meal(meal_id, title, *pairs, source="", instructions="Cook it.\r\nServe."):
    """A meal shaped like TheMealDB's response: 20 ingredient slots, unused ones empty."""
    meal = {"idMeal": str(meal_id), "strMeal": title, "strSource": source,
            "strInstructions": instructions, "strMealThumb": f"https://img/{meal_id}.jpg"}
    for slot in range(1, 21):
        name, measure = pairs[slot - 1] if slot <= len(pairs) else (None, None)
        meal[f"strIngredient{slot}"], meal[f"strMeasure{slot}"] = name, measure
    return meal


def accepted_items(*meals):
    """Run meals through the vocabulary and keep the accepted ones (what the import script passes in)."""
    return summarize(list(meals)).accepted


def test_seed_inserts_recipes_with_owner_ingredients_tags_and_text(session):
    items = accepted_items(
        make_meal(1, "Veg Stew", ("Carrots", "3"), ("Onion", "1"), ("Salt", "pinch")),
        make_meal(2, "Omelette", ("Eggs", "2"), ("Milk", "1 tbsp")),
    )
    result = seed(session, items)
    session.commit()

    assert result.inserted == 2 and result.skipped_existing == 0
    stew = session.scalar(select(Recipe).where(Recipe.title == "Veg Stew"))
    assert sorted(i.name for i in stew.ingredients) == ["carrot", "onion"]      # salt is not stored
    assert sorted(t.name for t in stew.dietary_tags) == ["dairy-free", "vegan", "vegetarian"]
    assert stew.owner.email == SEED_EMAIL
    assert stew.image_url == "https://img/1.jpg"
    assert stew.instructions.startswith("Ingredients:\n- 3 Carrots\n- 1 Onion\n- pinch Salt")
    omelette = session.scalar(select(Recipe).where(Recipe.title == "Omelette"))
    assert [t.name for t in omelette.dietary_tags] == ["vegetarian"]


def test_every_detectable_class_gets_a_row_even_if_no_recipe_uses_it(session):
    seed(session, accepted_items(make_meal(1, "Veg", ("Carrots", "1"))))
    session.commit()
    stored = {row.name for row in session.scalars(select(Ingredient))}
    assert stored == set(all_canonical_names())
    assert "dragon fruit" in stored and "salt" not in stored


def test_running_the_seed_twice_inserts_nothing_the_second_time(session):
    items = accepted_items(make_meal(1, "Veg", ("Carrots", "1")), make_meal(2, "Toast", ("Bread", "1")))
    first = seed(session, items)
    session.commit()
    second = seed(session, items)
    session.commit()
    assert first.inserted == 2 and second.inserted == 0 and second.skipped_existing == 2
    assert second.ingredients_created == 0 and second.tags_created == 0 and not second.user_created
    assert len(session.scalars(select(Recipe)).all()) == 2
    assert len(session.scalars(select(User)).all()) == 1


def test_two_recipes_with_the_same_source_url_in_one_run_insert_only_one(session):
    items = accepted_items(
        make_meal(1, "First", ("Carrots", "1"), source="https://same.example/page"),
        make_meal(2, "Second", ("Onion", "1"), source="https://same.example/page"),
    )
    result = seed(session, items)
    assert result.inserted == 1 and result.skipped_duplicate == ["Second"]


def test_plan_inserts_does_not_write_anything(session):
    plan = plan_inserts(session, accepted_items(make_meal(1, "Veg", ("Carrots", "1"))))
    assert len(plan.to_insert) == 1
    assert session.scalars(select(Recipe)).all() == [] and session.scalars(select(User)).all() == []

# ---------- the --commit flow
@pytest.fixture()
def patched_database(factory, monkeypatch):
    """Point the script at the in-memory database instead of the real one."""
    monkeypatch.setattr("app.core.database.SessionLocal", factory)
    return factory


def test_commit_writes_recipes_when_confirmed(patched_database, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")
    summary = summarize([make_meal(1, "Veg", ("Carrots", "1")), make_meal(2, "Toast", ("Bread", "1"))])
    commit_to_database(summary, failed_letters=[], assume_yes=False)
    with patched_database() as check:
        assert len(check.scalars(select(Recipe)).all()) == 2


def test_commit_writes_nothing_when_the_answer_is_not_yes(patched_database, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "no")
    commit_to_database(summarize([make_meal(1, "Veg", ("Carrots", "1"))]), failed_letters=[], assume_yes=False)
    with patched_database() as check:
        assert check.scalars(select(Recipe)).all() == [] and check.scalars(select(User)).all() == []


def test_commit_refuses_when_a_letter_failed_to_download(patched_database):
    summary = summarize([make_meal(1, "Veg", ("Carrots", "1"))])
    with pytest.raises(SystemExit, match="incomplete"):
        commit_to_database(summary, failed_letters=["c"], assume_yes=True)
    with patched_database() as check:
        assert check.scalars(select(Recipe)).all() == []


def test_commit_refuses_when_the_safety_scan_finds_a_problem(patched_database):
    from app.services.vocabulary import RecipeAnalysis
    wrong = {"meal": make_meal(1, "Bad Tag", ("Milk", "1 cup")), "pairs": [("Milk", "1 cup")],
             "analysis": RecipeAnalysis(True, [], ["dairy-free"], ["milk"])}   # milk is NOT dairy-free
    with pytest.raises(SystemExit, match="safety scan"):
        commit_to_database(Summary(total=1, accepted=[wrong]), failed_letters=[], assume_yes=True)
    with patched_database() as check:
        assert check.scalars(select(Recipe)).all() == []


def test_commit_twice_inserts_nothing_new(patched_database):
    summary = summarize([make_meal(1, "Veg", ("Carrots", "1"))])
    commit_to_database(summary, [], assume_yes=True)
    commit_to_database(summary, [], assume_yes=True)
    with patched_database() as check:
        assert len(check.scalars(select(Recipe)).all()) == 1


def test_a_failure_midway_rolls_everything_back(patched_database, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("simulated database failure")
    monkeypatch.setattr("scripts.seed_database.get_or_create_tags", explode)
    summary = summarize([make_meal(1, "Veg", ("Carrots", "1"))])
    with pytest.raises(RuntimeError):
        commit_to_database(summary, [], assume_yes=True)
    with patched_database() as check:
        assert check.scalars(select(User)).all() == [] and check.scalars(select(Recipe)).all() == []