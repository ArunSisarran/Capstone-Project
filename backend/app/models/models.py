import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

# many to many relationship for recipes and ingredients
recipe_ingredients = Table(
    "recipe_ingredients",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
)

recipe_dietary_tags = Table(
    "recipe_dietary_tags",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("dietary_tag_id", Integer, ForeignKey("dietary_tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    saved_recipes = relationship("SavedRecipe", back_populates="user")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    recipes = relationship("Recipe", secondary=recipe_ingredients, back_populates="ingredients")


class DietaryTag(Base):
    __tablename__ = "dietary_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    recipes = relationship("Recipe", secondary=recipe_dietary_tags, back_populates="dietary_tags")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    prep_time_minutes = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)
    source_url = Column(String, nullable=True)

    ingredients = relationship("Ingredient", secondary=recipe_ingredients, back_populates="recipes")
    dietary_tags = relationship("DietaryTag", secondary=recipe_dietary_tags, back_populates="recipes")
    saved_by = relationship("SavedRecipe", back_populates="recipe")


class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="saved_recipes")
    recipe = relationship("Recipe", back_populates="saved_by")