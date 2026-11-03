"""Input validation for recipes 
Pure schema tests: no database nor server"""
import pytest
from pydantic import ValidationError 

from app.schemas.schemas import RecipeUpdate

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