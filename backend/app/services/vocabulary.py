"""Ingredient vocabulary: turn raw recipe ingredient names into the canonical
classes Arun's model can detect, and work out dietary tags.

This module is pure logic. It never touches the database or FastAPI, which
makes it easy to test and lets several parts of the app share it:
  * the TheMealDB import script   (scripts/import_themealdb.py)
  * the photo recognition endpoint (maps detected class names to Ingredient rows)

Data lives in two reviewed CSV files in app/data/:
  * ingredient_vocabulary.csv - canonical classes, their aliases, dietary flags
  * staples.csv               - pantry items ignored for matching but still
                                checked for dietary tags (stock, soy sauce...)
"""
import csv
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

# Path(__file__) is this file, so the data folder is found no matter which
# directory the server or a script is started from (same idea as config.py).
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VOCAB_FILE = DATA_DIR / "ingredient_vocabulary.csv"
STAPLES_FILE = DATA_DIR / "staples.csv"

# (CSV column, name of the DietaryTag row in the database). Order is the order
# tags are returned in.
TAG_COLUMNS = (
    ("vegetarian", "vegetarian"),
    ("vegan", "vegan"),
    ("dairy_free", "dairy-free"),
)
VALID_FLAGS = {"yes", "no", "unsure"}


@dataclass(frozen=True)
class Record:
    """Everything we know about one ingredient. frozen=True makes it
    immutable, so one record can safely be shared by many aliases."""

    canonical: str             # "Bell Pepper", or the staple group name
    is_staple: bool            # True for rows from staples.csv
    ignore_for_matching: bool  # True for staples, and for Salt / Oil
    vegetarian: str            # "yes" | "no" | "unsure"
    vegan: str
    dairy_free: str


@dataclass(frozen=True)
class RecipeAnalysis:
    """Result of checking one whole recipe against the vocabulary."""

    accepted: bool         # True only if every ingredient was recognised
    unknown: list[str]     # raw names we could not resolve (why it was rejected)
    tags: list[str]        # e.g. ["vegetarian", "dairy-free"]
    canonical: list[str]   # lowercase class names to store as Ingredient rows


def normalize(raw: str) -> str:
    """Make different spellings of one ingredient compare equal.

    "  Crème Fraîche, " -> "creme fraiche"     "Free-Range Eggs" -> "free range eggs"
    """
    # NFKD splits "è" into "e" + an accent mark; we then drop the accent marks.
    text = unicodedata.normalize("NFKD", raw)
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    text = re.sub(r"[’'`]", "", text)        # za'atar -> zaatar
    text = re.sub(r"[^a-z0-9]+", " ", text)  # commas, hyphens, brackets -> space
    return text.strip()


def _read_rows(path: Path):
    # utf-8 matters: the CSVs contain accents, and Windows would otherwise
    # guess a different encoding. newline="" is what the csv module expects.
    with open(path, newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def _make_record(row: dict, *, is_staple: bool) -> Record:
    for column, _tag in TAG_COLUMNS:
        if row[column] not in VALID_FLAGS:
            name = row["group"] if is_staple else row["canonical"]
            raise ValueError(
                f"{name}: column '{column}' must be yes/no/unsure, got {row[column]!r}"
            )
    if is_staple:
        return Record(row["group"], True, True,
                      row["vegetarian"], row["vegan"], row["dairy_free"])
    return Record(row["canonical"], False, row["ignore_for_matching"] == "yes",
                  row["vegetarian"], row["vegan"], row["dairy_free"])


@lru_cache(maxsize=1)
def load_table() -> dict[str, Record]:
    """Read both CSVs once and return {normalized alias: Record}.

    lru_cache(maxsize=1) means the files are read on the first call only.
    """
    table: dict[str, Record] = {}
    for path, is_staple in ((VOCAB_FILE, False), (STAPLES_FILE, True)):
        for row in _read_rows(path):
            record = _make_record(row, is_staple=is_staple)
            for alias in row["aliases"].split(";"):
                # Normalize aliases with the SAME function used on lookups,
                # otherwise "free-range eggs" in the CSV could never match.
                key = normalize(alias)
                if not key:
                    continue
                # Two spellings of one class may collide after normalizing
                # ("creme fraiche" twice) - fine. Two DIFFERENT records
                # claiming one alias is a real data bug, so fail loudly.
                if key in table and table[key] != record:
                    raise ValueError(
                        f"alias {key!r} maps to both "
                        f"{table[key].canonical!r} and {record.canonical!r}"
                    )
                table[key] = record
    return table


def resolve(raw: str) -> Optional[Record]:
    """Look up one raw ingredient name. Returns None if it is unknown.

    Exact match first. If that fails, retry once without a trailing 'es' or
    's' so "tomatoes" -> "tomato". Anything smarter is deliberately avoided:
    a wrong guess is worse than a rejected recipe.
    """
    key = normalize(raw)
    if not key:
        return None
    table = load_table()
    candidates = [key]
    if key.endswith("es"):
        candidates.append(key[:-2])
    if key.endswith("s"):
        candidates.append(key[:-1])
    for candidate in candidates:
        if candidate in table:
            return table[candidate]
    return None


def derive_tags(records: Iterable[Record]) -> list[str]:
    """A recipe earns a tag only if EVERY ingredient is 'yes' for it.
    A single 'no' or 'unsure' removes the tag (fail closed)."""
    records = list(records)
    if not records:  # all() of nothing is True, which would tag an empty recipe
        return []
    return [
        tag for column, tag in TAG_COLUMNS
        if all(getattr(record, column) == "yes" for record in records)
    ]


def canonical_names(records: Iterable[Record]) -> list[str]:
    """Sorted, de-duplicated, lowercase class names to store as Ingredient
    rows. Staples and 'ignore for matching' items (Salt, Oil) are left out."""
    return sorted({
        record.canonical.lower()
        for record in records
        if not record.is_staple and not record.ignore_for_matching
    })


def analyze_recipe(raw_names: Iterable[str]) -> RecipeAnalysis:
    """Run a whole recipe's ingredient names through the vocabulary.

    Rejected when any name is unknown, or when nothing is left to match on
    (a recipe made only of staples can never be matched to a photo).
    """
    records: list[Record] = []
    unknown: list[str] = []
    for raw in raw_names:
        record = resolve(raw)
        if record is None:
            unknown.append(raw)
        else:
            records.append(record)
    canonical = canonical_names(records)
    accepted = not unknown and bool(canonical)
    tags = derive_tags(records) if accepted else []
    return RecipeAnalysis(accepted, unknown, tags, canonical if accepted else [])