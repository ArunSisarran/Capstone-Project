from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Recipe, SavedRecipe, User
from app.schemas.schemas import SavedKind, SavedRecipeOut

router = APIRouter(prefix="/saved-recipes", tags=["saved-recipes"])

# A recipe id in the URL: a positive whole number that fits the database's 32-bit column.
RecipeId = Annotated[int, Path(gt=0, lt=2**31)]


def _load_recipe_details():
    """Load each mark's recipe, its ingredients and its tags in a fixed number of queries."""
    return joinedload(SavedRecipe.recipe).options(
        selectinload(Recipe.ingredients),
        selectinload(Recipe.dietary_tags),
    )


def _find(db: Session, user_id, kind: str, recipe_id: int) -> Optional[SavedRecipe]:
    return (
        db.query(SavedRecipe)
        .options(_load_recipe_details())
        .filter(SavedRecipe.user_id == user_id, SavedRecipe.kind == kind, SavedRecipe.recipe_id == recipe_id)
        .first()
    )


@router.put("/{kind}/{recipe_id}", response_model=SavedRecipeOut)
def mark_recipe(
    kind: SavedKind,
    recipe_id: RecipeId,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a recipe as a favorite or as saved-for-later. Safe to repeat: marking twice changes nothing."""
    if db.get(Recipe, recipe_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    mark = _find(db, current_user.id, kind, recipe_id)
    if mark is None:
        db.add(SavedRecipe(user_id=current_user.id, recipe_id=recipe_id, kind=kind))
        try:
            db.commit()
        except IntegrityError:
            # Another request made the same mark a moment ago; the database refused the copy.
            db.rollback()
        mark = _find(db, current_user.id, kind, recipe_id)
    return mark


@router.delete("/{kind}/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def unmark_recipe(
    kind: SavedKind,
    recipe_id: RecipeId,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a mark. Safe to repeat: removing something that is not there is not an error."""
    db.query(SavedRecipe).filter(
        SavedRecipe.user_id == current_user.id,
        SavedRecipe.kind == kind,
        SavedRecipe.recipe_id == recipe_id,
    ).delete()
    db.commit()
    return None


@router.get("", response_model=List[SavedRecipeOut])
def list_marks(
    kind: Optional[SavedKind] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The current user's marks, newest first. Pass kind=favorite or kind=saved to filter."""
    query = (
        db.query(SavedRecipe)
        .options(_load_recipe_details())
        .filter(SavedRecipe.user_id == current_user.id)
    )
    if kind is not None:
        query = query.filter(SavedRecipe.kind == kind)
    return query.order_by(SavedRecipe.saved_at.desc(), SavedRecipe.id.desc()).offset(skip).limit(limit).all()