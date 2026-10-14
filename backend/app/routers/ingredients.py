from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Ingredient, User
from app.schemas.schemas import IngredientCreate, IngredientOut

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("", response_model=IngredientOut, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    payload: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Ingredient).filter(Ingredient.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredient already exists")

    ingredient = Ingredient(name=payload.name)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.get("", response_model=List[IngredientOut])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(Ingredient).order_by(Ingredient.name).all()