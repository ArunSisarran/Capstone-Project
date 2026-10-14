from datetime import datetime
import uuid
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field

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
   title: str
   instructions: str
   prep_time_minutes: Optional[int] = None
   image_url: Optional[str] = None
   source_url: Optional[str] = None
   ingredient_ids: List[int] = []
   dietary_tag_ids: List[int] = []

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    image_url: Optional[str] = None
    source_url: Optional[str] = None
    ingredient_ids: Optional[List[int]] = None
    dietary_tag_ids: Optional[List[int]] = None


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
   recipe_id: int

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


              