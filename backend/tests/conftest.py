"""Shared test setup.

Every test gets its own empty in-memory SQLite database. The DATABASE_URL line
below runs before any `app` import, so the real (Supabase) database in your
.env can never be reached from a test.
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("SECRET_KEY", "test-secret-not-used-for-anything-real")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def db(engine):
    """A session for arranging test data directly (commit after adding)."""
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture()
def client(engine):
    """A test client whose requests use the in-memory database."""
    factory = sessionmaker(bind=engine)

    def override_get_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()