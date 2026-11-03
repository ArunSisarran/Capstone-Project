"""Input validation for recipes 
Pure schema tests: no database nor server"""
import pytest
from pydantic import ValidationError 

from app.schemas.schemas import RecipeCreate, RecipeUpdate, SavedRecipeCreate

VALID = {"title": "Toast", "instructions": "Toast the bread."}

# ---------- PATCH: leaving a field out means "keep it", null means "error"
def test_an_update_with_nothing_set_changes_nothing():
    assert RecipeUpdate().model_dump(exclude_unset=True) == {}


@pytest.mark.parametrize("field", ["title", "instructions", "ingredient_ids", "dietary_tag_ids"])
def test_update_rejects_null_for_fields_the_database_requires(field):
    # F-05: this used to be a 500 from the database; it is now a clear 422.
    with pytest.raises(ValidationError):
        RecipeUpdate(**{field: None})


@pytest.mark.parametrize("field", ["prep_time_minutes", "image_url", "source_url"])
def test_update_still_allows_clearing_optional_fields(field):
    assert RecipeUpdate(**{field: None}).model_dump(exclude_unset=True) == {field: None}


@pytest.mark.parametrize("field", ["title", "instructions"])
def test_update_rejects_empty_text(field):
    with pytest.raises(ValidationError):
        RecipeUpdate(**{field: ""})


def test_update_accepts_ordinary_changes():
    update = RecipeUpdate(title="New title", ingredient_ids=[1, 2], prep_time_minutes=0)
    assert update.model_dump(exclude_unset=True) == {
        "title": "New title", "ingredient_ids": [1, 2], "prep_time_minutes": 0,
    }

# ---------- F-07: limits on what a client may send
@pytest.mark.parametrize("field", ["title", "instructions"])
def test_update_rejects_blank_text(field):
    with pytest.raises(ValidationError):
        RecipeUpdate(**{field: "   "})


@pytest.mark.parametrize("bad", [
    {"title": "x" * 201},
    {"prep_time_minutes": -1}, {"prep_time_minutes": 10001},
    {"image_url": "x" * 2001},
    {"ingredient_ids": [0]}, {"ingredient_ids": [2**31]},
    {"ingredient_ids": list(range(1, 102))},
    {"dietary_tag_ids": list(range(1, 22))},
])
def test_update_rejects_junk(bad):
    with pytest.raises(ValidationError):
        RecipeUpdate(**bad)


def test_a_minimal_recipe_is_valid_and_trims_whitespace():
    recipe = RecipeCreate(title="  Toast  ", instructions="Toast the bread.")
    assert recipe.title == "Toast"
    assert recipe.ingredient_ids == [] and recipe.dietary_tag_ids == []


@pytest.mark.parametrize("bad", [
    {"title": ""}, {"title": "   "}, {"title": "x" * 201},
    {"instructions": ""}, {"instructions": "   "},
    {"prep_time_minutes": -1}, {"prep_time_minutes": 10001},
    {"image_url": "x" * 2001},
    {"ingredient_ids": [0]}, {"ingredient_ids": [-5]}, {"ingredient_ids": [2**31]},
    {"ingredient_ids": list(range(1, 102))},
    {"dietary_tag_ids": list(range(1, 22))},
])
def test_create_rejects_junk(bad):
    with pytest.raises(ValidationError):
        RecipeCreate(**{**VALID, **bad})


def test_create_accepts_the_largest_legal_values():
    RecipeCreate(**VALID, prep_time_minutes=10000, ingredient_ids=[2**31 - 1] * 100)


@pytest.mark.parametrize("recipe_id", [0, -1, 2**31])
def test_saving_a_recipe_rejects_ids_that_cannot_exist(recipe_id):
    # a number beyond a 32-bit column would otherwise reach PostgreSQL and fail with a 500
    with pytest.raises(ValidationError):
        SavedRecipeCreate(recipe_id=recipe_id)    