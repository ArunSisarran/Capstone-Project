"""Rehearse the saved_recipes migration on a THROWAWAY SQLite file. Never touches your real database.

Run from backend/ with the venv active:   python rehearse_migration.py
"""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

DB_FILE = Path("/tmp/rehearsal_old.db")
MIGRATION = Path("alembic/versions/e1b7c4a90d52_add_kind_to_saved_recipes.py")


def alembic(*args):
    """Run an alembic command against the throwaway database. Returns (ok, last line of output)."""
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{DB_FILE}"}
    env.setdefault("SECRET_KEY", "rehearsal-only")
    run = subprocess.run([sys.executable, "-m", "alembic", *args], env=env, capture_output=True, text=True)
    lines = (run.stdout + run.stderr).strip().splitlines()
    return run.returncode == 0, (lines[-1] if lines else "")


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   ({detail})" if detail else ""))
    return ok


def main():
    if not Path("alembic.ini").exists():
        sys.exit("Run this from the backend/ folder (the one containing alembic.ini).")
    if not MIGRATION.exists():
        sys.exit(f"The migration file is missing: {MIGRATION}\nCopy it into alembic/versions/ first.")

    # An old-style saved_recipes table: no 'kind' column, and one accidental duplicate row.
    DB_FILE.unlink(missing_ok=True)
    db = sqlite3.connect(DB_FILE)
    db.executescript("""
        CREATE TABLE users (id CHAR(32) PRIMARY KEY, email VARCHAR NOT NULL, hashed_password VARCHAR NOT NULL);
        CREATE TABLE recipes (id INTEGER PRIMARY KEY, title VARCHAR NOT NULL);
        CREATE TABLE saved_recipes (
          id INTEGER PRIMARY KEY,
          user_id CHAR(32) NOT NULL REFERENCES users(id),
          recipe_id INTEGER NOT NULL REFERENCES recipes(id),
          saved_at DATETIME
        );
        INSERT INTO users VALUES ('u1', 'a@example.com', 'x');
        INSERT INTO recipes VALUES (1, 'R1'), (2, 'R2');
        INSERT INTO saved_recipes (user_id, recipe_id) VALUES ('u1', 1), ('u1', 1), ('u1', 2);
    """)
    db.commit()
    db.close()
    print("Rehearsal on a throwaway database (old table: 3 rows, one is a duplicate)\n")

    results = []
    ok, _ = alembic("stamp", "71be6535529c")
    results.append(check("start from the current version (71be6535529c)", ok))

    ok, head = alembic("heads")
    results.append(check("alembic can see the new migration", "e1b7c4a90d52" in head, head))

    ok, _ = alembic("upgrade", "head")
    results.append(check("upgrade runs without errors", ok))

    db = sqlite3.connect(DB_FILE)
    rows = db.execute("SELECT recipe_id, kind FROM saved_recipes ORDER BY id").fetchall()
    sql = db.execute("SELECT sql FROM sqlite_master WHERE name='saved_recipes'").fetchone()[0]
    results.append(check("the duplicate row was removed, old rows became 'saved'", rows == [(1, "saved"), (2, "saved")], str(rows)))
    results.append(check("the unique rule and the kind rule exist", "uq_saved_user_recipe_kind" in sql and "ck_saved_kind" in sql))
    for kind, should_work in (("favorite", True), ("bookmark", False)):
        try:
            db.execute("INSERT INTO saved_recipes (user_id, recipe_id, kind) VALUES ('u1', 2, ?)", (kind,))
            worked = True
        except sqlite3.IntegrityError:
            worked = False
        results.append(check(f"kind {kind!r} is {'accepted' if should_work else 'rejected'}", worked == should_work))
    try:
        db.execute("INSERT INTO saved_recipes (user_id, recipe_id, kind) VALUES ('u1', 1, 'saved')")
        duplicate_worked = True
    except sqlite3.IntegrityError:
        duplicate_worked = False
    results.append(check("a duplicate 'saved' mark is rejected", not duplicate_worked))
    db.close()

    ok, _ = alembic("downgrade", "-1")
    results.append(check("downgrade (undo) runs without errors", ok))
    ok, head = alembic("upgrade", "head")
    results.append(check("upgrade again works", ok))
    ok, head = alembic("heads")
    results.append(check("exactly one head: e1b7c4a90d52", head.startswith("e1b7c4a90d52"), head))

    DB_FILE.unlink(missing_ok=True)
    print("\n" + ("ALL GOOD: the migration is safe to use." if all(results) else "SOMETHING FAILED: do not touch the real database. Paste this output to me."))


main()