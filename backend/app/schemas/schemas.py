from datetime import datetime
import uuid
from typing import Annotated, Optional, List


from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# A database id: a positive whole number that fits the database's 32-bit integer column.
DbId = Annotated[int, Field(gt=0, lt=2**31)]

class UserCreate(BaseModel):
  email: EmailStr
  password: str = Field(min_length=12)

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  

class Token(BaseModel):
   access_token: str
   token_type: str = "bearer"

class LoginRequest(BaseModel):
   email: EmailStr
   password: str

class IngredientOut(BaseModel):
   id: int
   name: str

   class Config:
      from_attributes = True

class DietaryTagOut(BaseModel):
   id: int
   name: str

   class Config:
      from_attributes = True

class RecipeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)   # "   " must not count as a title

    title: str = Field(min_length=1, max_length=200)
    instructions: str = Field(min_length=1, max_length=20000)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0, le=10000)
    image_url: Optional[str] = Field(default=None, max_length=2000)
    source_url: Optional[str] = Field(default=None, max_length=2000)
    ingredient_ids: List[DbId] = Field(default=[], max_length=100)
    dietary_tag_ids: List[DbId] = Field(default=[], max_length=20)

class RecipeUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    instructions: Optional[str] = Field(default=None, min_length=1, max_length=20000)
    prep_time_minutes: Optional[int] = Field(default=None, ge=0, le=10000)
    image_url: Optional[str] = Field(default=None, max_length=2000)
    source_url: Optional[str] = Field(default=None, max_length=2000)
    ingredient_ids: Optional[List[DbId]] = Field(default=None, max_length=100)
    dietary_tag_ids: Optional[List[DbId]] = Field(default=None, max_length=20)

    @field_validator("title", "instructions", "ingredient_ids", "dietary_tag_ids")
    @classmethod
    def reject_explicit_null(cls, value):
        # Leaving a field out means "keep it". Sending null would try to blank a column
        # the database requires, which used to crash with a 500 instead of a clear 422.
        if value is None:
            raise ValueError("cannot be null; leave the field out to keep its current value")
        return value


class RecipeOut(BaseModel):
    id: int
    title: str
    instructions: str
    prep_time_minutes: Optional[int]
    image_url: Optional[str]
    source_url: Optional[str]
    ingredients: List[IngredientOut] = []
    dietary_tags: List[DietaryTagOut] = []

    class Config:
        from_attributes = True  

class SavedRecipeCreate(BaseModel):
   recipe_id: DbId

class SavedRecipeOut(BaseModel):
   id: int
   recipe_id: int
   saved_at: datetime
   recipe: RecipeOut

   class Config:
      from_attributes = True        

class IngredientCreate(BaseModel):
   name: str

class DietaryTagCreate(BaseModel):
   name: str            

class UserUpdate(BaseModel):
   email: Optional[EmailStr] = None

class PasswordChange(BaseModel): 
   current_password: str
   new_password: str = Field(min_length=12)

class RecipeMatchOut(RecipeOut):
   matched_count: int = 0
   match_score: float = 0.0
   total_ingredients: int = 0
   missing_ingredients: List[IngredientOut] = []