from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import SavedRecipe, Recipe, User
from app.schemas.schemas import SavedRecipeCreate, SavedRecipeOut

router = APIRouter(prefix="/saved-recipes", tags=["saved-recipes"])


@router.post("", response_model=SavedRecipeOut, status_code=status.HTTP_201_CREATED)
def save_recipe(
    payload: SavedRecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.query(Recipe).filter(Recipe.id == payload.recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    existing = (
        db.query(SavedRecipe)
        .filter(SavedRecipe.user_id == current_user.id, SavedRecipe.recipe_id == payload.recipe_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipe already saved")

    saved = SavedRecipe(user_id=current_user.id, recipe_id=payload.recipe_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("", response_model=List[SavedRecipeOut])
def list_saved_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(SavedRecipe)
        .options(joinedload(SavedRecipe.recipe))
        .filter(SavedRecipe.user_id == current_user.id)
        .all()
    )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved = (
        db.query(SavedRecipe)
        .filter(SavedRecipe.user_id == current_user.id, SavedRecipe.recipe_id == recipe_id)
        .first()
    )
    if saved is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved recipe not found")

    db.delete(saved)
    db.commit()
    return None