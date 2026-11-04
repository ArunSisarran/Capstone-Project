"""Dry-run import of TheMealDB recipes against our ingredient vocabulary.

THIS VERSION NEVER WRITES TO THE DATABASE. It fetches recipes, checks every
ingredient against app/services/vocabulary.py, and prints a report so you can
tune the CSV files before anything is inserted.

Run from backend/ with the venv active:

    python -m scripts.import_themealdb                  # all letters a-z
    python -m scripts.import_themealdb --letters ab     # just a and b (quick test)
    python -m scripts.import_themealdb --refresh        # ignore cached downloads
    python -m scripts.import_themealdb --top 50 --samples 20
    python -m scripts.import_themealdb --tag vegan      # list EVERY accepted vegan recipe to audit

    To WRITE the accepted recipes to the database in DATABASE_URL (it asks first):

    python -m scripts.import_themealdb --commit

--commit refuses to run if any letter failed to download or if the safety scan
found a problem. It prints which database it will write to (never the
password) and waits for you to type "yes". Running it twice is safe: recipes
whose source_url already exists are skipped. The database is SHARED, so tell
your teammates before you run it.
Downloads are cached in scripts/cache/ (gitignored), so re-running after you
edit the CSVs does not hit the API again.

Before using real data, read TheMealDB's terms at https://www.themealdb.com/api.php
(the free test key "1" is meant for development / educational use, and the
site asks for credit when you display its recipes).
"""
import argparse
import json
import random
import string
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from app.services.vocabulary import RecipeAnalysis, analyze_recipe, normalize

BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php"
CACHE_DIR = Path(__file__).resolve().parent / "cache"
USER_AGENT = "recipe-recommender-capstone/0.1 (class project)"
MAX_INGREDIENT_SLOTS = 20          # the API has strIngredient1 .. strIngredient20
PAUSE_BETWEEN_REQUESTS = 0.5       # seconds; be polite to a free API


# ----------------------------------------------------------------- fetching
def fetch_letter(letter: str, refresh: bool = False) -> list[dict] | None:
    """All meals whose name starts with `letter`.

    Returns [] for a letter with no meals, and None if the download failed
    (so the caller can warn instead of silently losing data).
    """
    cache_file = CACHE_DIR / f"{letter}.json"
    if cache_file.exists() and not refresh:
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
    else:
        request = urllib.request.Request(
            f"{BASE_URL}?f={letter}", headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            print(f"  ! could not fetch letter {letter!r}: {error}")
            return None
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(payload), encoding="utf-8")
        time.sleep(PAUSE_BETWEEN_REQUESTS)
    # The API answers {"meals": null} when nothing matches.
    return payload.get("meals") or []


# --------------------------------------------------------------- extracting
def extract_ingredients(meal: dict) -> list[tuple[str, str]]:
    """[(ingredient name, measure), ...] for the non-blank slots of one meal."""
    pairs = []
    for slot in range(1, MAX_INGREDIENT_SLOTS + 1):
        name = (meal.get(f"strIngredient{slot}") or "").strip()
        if name:
            measure = (meal.get(f"strMeasure{slot}") or "").strip()
            pairs.append((name, measure))
    return pairs


# ---------------------------------------------------------------- analysing
@dataclass
class Summary:
    total: int = 0
    accepted: list[dict] = field(default_factory=list)   # {"meal","pairs","analysis"}
    rejected: list[dict] = field(default_factory=list)
    blocks: Counter = field(default_factory=Counter)     # name -> rejected recipes it appears in
    unlocks: Counter = field(default_factory=Counter)    # name -> recipes that pass if only this is added
    tag_counts: Counter = field(default_factory=Counter)
    unknown_per_recipe: Counter = field(default_factory=Counter)  # 1, 2, or 3 (= 3 or more)


def summarize(meals: list[dict]) -> Summary:
    """Run every meal through the vocabulary and collect the numbers."""
    summary = Summary()
    seen_ids = set()
    for meal in meals:
        meal_id = meal.get("idMeal")
        if meal_id in seen_ids:           # a-z searches should not overlap, but be safe
            continue
        seen_ids.add(meal_id)
        summary.total += 1

        pairs = extract_ingredients(meal)
        analysis: RecipeAnalysis = analyze_recipe([name for name, _ in pairs])
        item = {"meal": meal, "pairs": pairs, "analysis": analysis}

        if analysis.accepted:
            summary.accepted.append(item)
            for tag in analysis.tags:
                summary.tag_counts[tag] += 1
            if not analysis.tags:
                summary.tag_counts["(no tags)"] += 1
        else:
            summary.rejected.append(item)
            # count each distinct unknown name once per recipe
            names = {normalize(name) for name in analysis.unknown}
            if names:                     # a recipe with NO unknown names was rejected for another reason
                summary.unknown_per_recipe[min(len(names), 3)] += 1
            for name in names:
                summary.blocks[name] += 1
            if len(names) == 1:           # this one name is the ONLY thing blocking the recipe
                summary.unlocks[next(iter(names))] += 1
    return summary


# ------------------------------------------------------------ safety scan
# An INDEPENDENT check on the dietary tags. It knows nothing about the CSV
# flags: it just looks for plain-English red-flag words in the ingredient names
# of recipes that carry a tag. If the CSV is wrong somewhere, this catches it.
MEAT_FISH_WORDS = {
    "chicken", "beef", "pork", "lamb", "mutton", "veal", "venison", "bacon", "ham", "gammon",
    "sausage", "sausages", "chorizo", "salami", "pepperoni", "prosciutto", "steak", "mince",
    "oxtail", "brisket", "turkey", "duck", "goose", "rabbit", "liver", "kidney", "tripe",
    "fish", "salmon", "cod", "tuna", "haddock", "sardine", "sardines", "mackerel", "trout",
    "anchovy", "anchovies", "prawn", "prawns", "shrimp", "squid", "crab", "lobster",
    "mussel", "mussels", "clam", "clams", "oyster", "oysters",
    "gelatin", "gelatine", "lard", "suet", "dripping", "tallow", "worcestershire",
}
DAIRY_WORDS = {
    "milk", "buttermilk", "butter", "cheese", "cheddar", "mozzarella", "parmesan", "feta",
    "ricotta", "mascarpone", "halloumi", "paneer", "cream", "yogurt", "yoghurt", "ghee",
    "whey", "casein", "custard",
}
EGG_HONEY_WORDS = {"egg", "eggs", "honey", "mayonnaise", "mayo"}
RED_FLAG_WORDS = {
    "vegetarian": MEAT_FISH_WORDS,
    "dairy-free": DAIRY_WORDS,
    "vegan": MEAT_FISH_WORDS | DAIRY_WORDS | EGG_HONEY_WORDS,
}
# Phrases that contain a red-flag word but are fine. Removed before scanning.
SAFE_PHRASES = [
    "coconut milk", "coconut cream", "creamed coconut", "almond milk", "soy milk", "soya milk",
    "oat milk", "rice milk", "peanut butter", "almond butter", "nut butter", "cocoa butter",
    "shea butter", "butter beans", "butter bean", "cream of tartar",
    "kidney beans", "kidney bean", "egg plants", "egg plant",
]


def red_flags(names: list[str], tags: list[str]) -> list[tuple[str, str]]:
    """[(tag, word)] for every red-flag word found in `names` for the given tags."""
    words: set[str] = set()
    for name in names:
        text = f" {normalize(name)} "
        for phrase in SAFE_PHRASES:
            text = text.replace(f" {phrase} ", " ")
        words.update(text.split())
    hits = []
    for tag in tags:
        for word in sorted(RED_FLAG_WORDS.get(tag, ())):
            if word in words:
                hits.append((tag, word))
    return hits


def scan_accepted(summary: "Summary") -> list[tuple[str, str, str]]:
    """[(recipe title, tag, word)] for tagged recipes that contain a red-flag word."""
    suspects = []
    for item in summary.accepted:
        names = [name for name, _ in item["pairs"]]
        for tag, word in red_flags(names, item["analysis"].tags):
            suspects.append((item["meal"].get("strMeal", "?"), tag, word))
    return suspects


# ---------------------------------------------------------------- reporting
def accepted_with_tag(summary: Summary, tag: str) -> list[dict]:
    """Every accepted recipe that earned `tag` (used to audit a tag by hand)."""
    return [item for item in summary.accepted if tag in item["analysis"].tags]


def print_recipe(item: dict) -> None:
    analysis = item["analysis"]
    print(f"\n  {item['meal'].get('strMeal', '?')}")
    for name, measure in item["pairs"]:
        print(f"      {measure:14} {name}")
    print(f"    -> matches on: {', '.join(analysis.canonical)}")
    print(f"    -> tags: {', '.join(analysis.tags) or '(none)'}")


def print_report(summary: Summary, top: int, samples: int, tag: str | None = None) -> None:
    total = summary.total
    passed = len(summary.accepted)
    percent = (100 * passed / total) if total else 0.0
    print("\n" + "=" * 64)
    print(f"Recipes read: {total}   accepted: {passed} ({percent:.0f}%)   rejected: {len(summary.rejected)}")
    print("=" * 64)

    print("\nRejected recipes by how many unknown ingredients they contain")
    print("  (recipes with 1 are the closest to being accepted)")
    for count, label in ((1, "1 unknown"), (2, "2 unknown"), (3, "3 or more")):
        print(f"  {label:10} {summary.unknown_per_recipe.get(count, 0)}")
    only_staples = len(summary.rejected) - sum(summary.unknown_per_recipe.values())
    if only_staples:
        print(f"  (no unknowns, but nothing left to match on: {only_staples})")

    print(f"\nTop {top} unknown ingredients")
    print("  blocks  = rejected recipes that contain it")
    print("  unlocks = recipes that would be ACCEPTED if only this one were added")
    print(f"  {'ingredient':32} {'blocks':>6} {'unlocks':>8}")
    for name, count in summary.blocks.most_common(top):
        print(f"  {name:32} {count:>6} {summary.unlocks.get(name, 0):>8}")

    print("\nDietary tags among accepted recipes")
    for tag_name, count in summary.tag_counts.most_common():   # NOT `tag`: that is the --tag option
        print(f"  {tag_name:12} {count}")

    suspects = scan_accepted(summary)
    print("\nSafety scan (independent of the CSV flags)")
    if suspects:
        print(f"  !! {len(suspects)} tagged recipe(s) contain a red-flag word. Check these FIRST:")
        for title, tag_name, word in suspects:
            print(f"     {title}: tagged '{tag_name}' but contains '{word}'")
    else:
        print("  OK: no tagged recipe contains a red-flag word for a tag it carries.")

    if tag:
        audit = accepted_with_tag(summary, tag)
        print(f"\nAUDIT: all {len(audit)} accepted recipes tagged '{tag}'.")
        print("  Read each ingredient list. Any animal product or doubtful ingredient means")
        print("  a CSV flag is wrong - fix it there, never by hand-editing the database.")
        for item in audit:
            print_recipe(item)
        return

    print(f"\n{min(samples, passed)} accepted recipes to check by hand")
    for item in random.Random(42).sample(summary.accepted, min(samples, passed)):
        print_recipe(item)

# ------------------------------------------------------------------- commit
def commit_to_database(summary: Summary, failed_letters: list[str], assume_yes: bool,
                       seed_email: str | None = None) -> None:
    """Write the accepted recipes to the database in DATABASE_URL, after safety checks."""
    if failed_letters:
        raise SystemExit("Refusing to commit: these letters failed to download, so the data is "
                         f"incomplete ({', '.join(failed_letters)}). Run again first.")
    suspects = scan_accepted(summary)
    if suspects:
        raise SystemExit(f"Refusing to commit: the safety scan flagged {len(suspects)} recipe(s). "
                         "Fix the CSV flags first (see the 'Safety scan' section above).")

    # Imported here, not at the top, so the dry run and the tests never need a database.
    from sqlalchemy.engine import make_url
    from app.core import database
    from app.core.config import settings
    from scripts.seed_database import SEED_EMAIL, plan_inserts, seed

    url = make_url(settings.database_url)
    target = f"{url.host or '(local file)'}/{url.database or ''}"
    session = database.SessionLocal()
    try:
        plan = plan_inserts(session, summary.accepted)
        print("\n" + "=" * 64)
        print(f"COMMIT to database: {target}")
        print(f"  new recipes to insert:      {len(plan.to_insert)}")
        print(f"  already in the database:    {plan.skipped_existing}")
        print(f"  duplicate source_url (skip): {len(plan.skipped_duplicate)}")
        print("  also ensures: the seed user, 3 dietary tags, and one ingredient row per detectable class")
        print("=" * 64)
        if not assume_yes and input('Type "yes" to write these to the database: ').strip().lower() != "yes":
            print("Cancelled. Nothing was written.")
            return
        result = seed(session, summary.accepted, seed_email or SEED_EMAIL)
        session.commit()
        print(f"\nDone. inserted {result.inserted} recipes, skipped {result.skipped_existing} existing, "
              f"created {result.ingredients_created} ingredients and {result.tags_created} tags"
              f"{', created the seed user' if result.user_created else ''}.")
        for title in result.skipped_duplicate:
            print(f"  skipped (same source_url as another recipe): {title}")
    except Exception:
        session.rollback()          # all-or-nothing: a failure leaves the database untouched
        raise
    finally:
        session.close()
# --------------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--letters", default=string.ascii_lowercase,
                        help="which first letters to fetch (default: a-z)")
    parser.add_argument("--refresh", action="store_true", help="ignore cached downloads")
    parser.add_argument("--top", type=int, default=30, help="unknown ingredients to list")
    parser.add_argument("--samples", type=int, default=10, help="accepted recipes to print")
    parser.add_argument("--tag", choices=["vegetarian", "vegan", "dairy-free"],
                        help="print EVERY accepted recipe with this tag, to audit it by hand")
    parser.add_argument("--commit", action="store_true",
                        help="WRITE the accepted recipes to the database in DATABASE_URL (asks first)")
    parser.add_argument("--yes", action="store_true", help="with --commit: do not ask for confirmation")
    parser.add_argument("--seed-email", default=None, help="email of the account that owns imported recipes")
    parser.add_argument("--dry-run", action="store_true",
                        help="accepted for clarity; this version never writes to the database")
    args = parser.parse_args()

    meals: list[dict] = []
    failed: list[str] = []
    for letter in args.letters.lower():
        batch = fetch_letter(letter, refresh=args.refresh)
        if batch is None:
            failed.append(letter)
        else:
            meals.extend(batch)
            print(f"  letter {letter}: {len(batch)} meals")

    summary = summarize(meals)
    print_report(summary, top=args.top, samples=args.samples, tag=args.tag)
    if failed:
        print(f"\n! These letters failed to download and are NOT in the numbers: {', '.join(failed)}")
        print("  Check your internet connection and run again.")

        if args.commit:
            commit_to_database(summary, failed, assume_yes=args.yes, seed_email=args.seed_email)    

if __name__ == "__main__":
    main()
