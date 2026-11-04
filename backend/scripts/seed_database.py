"""Write accepted TheMealDB recipes into the database.

Used by `python -m scripts.import_themealdb --commit`. Nothing here talks to
the network. (Built up section by section.)
"""
import secrets
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.models import DietaryTag, Ingredient, Recipe, User
from app.services.vocabulary import TAG_COLUMNS, all_canonical_names

SEED_EMAIL = "seed-bot@recipe-recommender.dev"
CREDIT_LINE = "Recipe from TheMealDB (https://www.themealdb.com)"
# TheMealDB's own source field is often empty. This documented lookup URL is
# unique per meal, so it keeps source_url unique. Swap in the website's page
# address here once you have confirmed what that looks like in your browser.
FALLBACK_SOURCE_URL = "https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"


def build_source_url(meal: dict) -> str:
    """The recipe's own source page if it has one, otherwise the fallback."""
    own = (meal.get("strSource") or "").strip()
    return own or FALLBACK_SOURCE_URL.format(meal_id=meal["idMeal"])


def build_instructions(meal: dict, pairs: list[tuple[str, str]]) -> str:
    """Instructions text. The ORIGINAL ingredient lines go first, because the
    database stores only canonical class names and no quantities."""
    lines = [f"- {measure} {name}" if measure else f"- {name}" for name, measure in pairs]
    body = (meal.get("strInstructions") or "").replace("\r\n", "\n").strip() or "(No instructions provided.)"
    return "Ingredients:\n" + "\n".join(lines) + "\n\nInstructions:\n" + body + "\n\n" + CREDIT_LINE

# ------------------------------------------------------------ get-or-create
def get_or_create_seed_user(session: Session, email: str = SEED_EMAIL) -> tuple[User, bool]:
    user = session.scalar(select(User).where(User.email == email))
    if user:
        return user, False
    # Random password nobody ever sees: this account owns data, it never logs in.
    user = User(email=email, hashed_password=hash_password(secrets.token_urlsafe(32)))
    session.add(user)
    session.flush()
    return user, True


def get_or_create_tags(session: Session) -> tuple[dict[str, DietaryTag], int]:
    existing = {tag.name.lower(): tag for tag in session.scalars(select(DietaryTag))}
    created = 0
    for _column, name in TAG_COLUMNS:
        if name not in existing:
            existing[name] = DietaryTag(name=name)
            session.add(existing[name])
            created += 1
    session.flush()
    return existing, created


def get_or_create_ingredients(session: Session, names: list[str]) -> tuple[dict[str, Ingredient], int]:
    existing = {row.name.lower(): row for row in session.scalars(select(Ingredient))}
    created = 0
    for name in names:
        if name not in existing:
            existing[name] = Ingredient(name=name)
            session.add(existing[name])
            created += 1
    session.flush()
    return existing, created

# ----------------------------------------------------------------- planning
@dataclass
class Plan:
    to_insert: list[dict] = field(default_factory=list)          # recipes that are new
    skipped_existing: int = 0                                    # source_url already in the database
    skipped_duplicate: list[str] = field(default_factory=list)   # same source_url twice in this run


def plan_inserts(session: Session, items: list[dict]) -> Plan:
    """READ-ONLY: which of the accepted recipes would be new?"""
    in_database = {url for url in session.scalars(select(Recipe.source_url)) if url}
    in_this_run: set[str] = set()
    plan = Plan()
    for item in items:
        url = build_source_url(item["meal"])
        if url in in_database:
            plan.skipped_existing += 1
        elif url in in_this_run:
            plan.skipped_duplicate.append(item["meal"].get("strMeal", url))
        else:
            in_this_run.add(url)
            plan.to_insert.append(item)
    return plan

@dataclass
class SeedResult:
    inserted: int = 0
    skipped_existing: int = 0
    skipped_duplicate: list[str] = field(default_factory=list)
    ingredients_created: int = 0
    tags_created: int = 0
    user_created: bool = False


def seed(session: Session, items: list[dict], seed_email: str = SEED_EMAIL) -> SeedResult:
    """Insert every new accepted recipe. Flushes only; the caller commits."""
    result = SeedResult()
    owner, result.user_created = get_or_create_seed_user(session, seed_email)
    tags, result.tags_created = get_or_create_tags(session)
    ingredients, result.ingredients_created = get_or_create_ingredients(session, all_canonical_names())

    plan = plan_inserts(session, items)
    result.skipped_existing = plan.skipped_existing
    result.skipped_duplicate = plan.skipped_duplicate

    for item in plan.to_insert:
        meal, analysis = item["meal"], item["analysis"]
        session.add(Recipe(
            title=meal["strMeal"],
            instructions=build_instructions(meal, item["pairs"]),
            prep_time_minutes=None,
            image_url=(meal.get("strMealThumb") or None),
            source_url=build_source_url(meal),
            owner_id=owner.id,
            ingredients=[ingredients[name] for name in analysis.canonical],
            dietary_tags=[tags[name] for name in analysis.tags],
        ))
        result.inserted += 1
    session.flush()
    return result