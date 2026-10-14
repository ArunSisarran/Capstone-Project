from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import DietaryTag, User
from app.schemas.schemas import DietaryTagCreate, DietaryTagOut

router = APIRouter(prefix="/dietary-tags", tags=["dietary-tags"])


@router.post("", response_model=DietaryTagOut, status_code=status.HTTP_201_CREATED)
def create_dietary_tag(
    payload: DietaryTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(DietaryTag).filter(DietaryTag.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dietary tag already exists")

    tag = DietaryTag(name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("", response_model=List[DietaryTagOut])
def list_dietary_tags(db: Session = Depends(get_db)):
    return db.query(DietaryTag).order_by(DietaryTag.name).all()