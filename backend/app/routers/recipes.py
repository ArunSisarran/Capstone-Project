from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.models import Recipe, Ingredient, DietaryTag, User
from app.schemas.schemas import RecipeCreate, RecipeOut, RecipeUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("", response_model=List[RecipeOut])
def list_recipes(
  skip: int = 0,
  limit: int = 20,
  ingredient_id: Optional[int] = None,
  dietary_tag_id: Optional[int] = None,
  db: Session = Depends(get_db)
):
  query = db.query(Recipe).options(
    joinedload(Recipe.ingredients),
    joinedload(Recipe.dietary_tags),
  )

  if ingredient_id is not None:
    query = query.filter(Recipe.ingredients.any(Ingredient.id == ingredient_id))
  if dietary_tag_id is not None:
    query = query.filter(Recipe.dietary_tags.any(DietaryTag.id == dietary_tag_id))

  recipes = query.offset(skip).limit(limit).all()
  return recipes

@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = (
        db.query(Recipe)
        .options(joinedload(Recipe.ingredients), joinedload(Recipe.dietary_tags))
        .filter(Recipe.id == recipe_id)
        .first()
    )

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    return recipe

@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
def create_recipe(
   recipe_in: RecipeCreate,
   db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user),
):
   ingredients = db.query(Ingredient).filter(Ingredient.id.in_(recipe_in.ingredient_ids)).all()
   if len(ingredients) != len(set(recipe_in.ingredient_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more ingredient_ids do not exist",
        )
   
   dietary_tags = db.query(DietaryTag).filter(DietaryTag.id.in_(recipe_in.dietary_tag_ids)).all()
   if len(dietary_tags) != len(set(recipe_in.dietary_tag_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more dietary_tag_ids do not exist",
        )
   
   recipe = Recipe(
      title=recipe_in.title,
      instructions=recipe_in.instructions,
      prep_time_minutes=recipe_in.prep_time_minutes,
      image_url=recipe_in.image_url,
      source_url=recipe_in.source_url,
      owner_id=current_user.id,
      ingredients=ingredients,
      dietary_tags=dietary_tags,
      )
   db.add(recipe)
   db.commit()
   db.refresh(recipe)
   return recipe

@router.patch("/{recipe_id}", response_model=RecipeOut)
def update_recipe(
   recipe_id: int,
   recipe_in: RecipeUpdate,
   db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user),
): 
   recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

   if recipe is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

   if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this recipe")
   
   update_data = recipe_in.model_dump(exclude_unset=True)
   
   if "ingredient_ids" in update_data:
        ids = update_data.pop("ingredient_ids")
        ingredients = db.query(Ingredient).filter(Ingredient.id.in_(ids)).all()
        if len(ingredients) != len(set(ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more ingredient_ids do not exist")
        recipe.ingredients = ingredients
        
   if "dietary_tag_ids" in update_data:
        ids = update_data.pop("dietary_tag_ids")
        tags = db.query(DietaryTag).filter(DietaryTag.id.in_(ids)).all()
        if len(tags) != len(set(ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more dietary_tag_ids do not exist")
        recipe.dietary_tags = tags

   for field, value in update_data.items():
        setattr(recipe, field, value)

   db.commit()
   db.refresh(recipe)
   return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this recipe")

    db.delete(recipe)
    db.commit()
    return None