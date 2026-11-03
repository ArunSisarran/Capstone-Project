"""Regression tests for the auth dependency 

get_current_user is called directly, with an in-memory SQLite 
database, so these tests need no running server and can never
 touch the real database
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("SECRET_KEY", "test-secret-not-used-for-anything-real")

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base
from app.core.security import create_access_token, get_current_user
from app.models.models import User

@pytest.fixture()
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    yield db
    db.close()


def credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def signed(claims: dict) -> str:
    return jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)


def in_one_hour() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)


def assert_rejected(session, token: str):
    with pytest.raises(HTTPException) as caught:
        get_current_user(credentials(token), session)
    assert caught.value.status_code == 401
    assert caught.value.headers["WWW-Authenticate"] == "Bearer"
    
def test_a_valid_token_returns_its_user(session):
    # Before the fix this raised an AttributeError on SQLite, because the id from the
    # token is text but the column is a UUID. (PostgreSQL happened to coerce it.)
    user = User(email="a@example.com", hashed_password="not-a-real-hash")
    session.add(user)
    session.commit()
    result = get_current_user(credentials(create_access_token(str(user.id))), session)
    assert result.id == user.id and result.email == "a@example.com"

def test_a_token_for_a_user_that_no_longer_exists_is_rejected(session):
    import uuid
    assert_rejected(session, create_access_token(str(uuid.uuid4())))


@pytest.mark.parametrize("subject", ["not-a-uuid", "", "12345", "' OR 1=1 --"])
def test_a_malformed_subject_is_a_401_not_a_crash(session, subject):
    assert_rejected(session, create_access_token(subject))


def test_a_non_text_subject_is_a_401(session):
    assert_rejected(session, signed({"sub": 12345, "exp": in_one_hour()}))


def test_a_token_without_a_subject_is_a_401(session):
    assert_rejected(session, signed({"exp": in_one_hour()}))


def test_an_expired_token_is_a_401(session):
    user = User(email="b@example.com", hashed_password="not-a-real-hash")
    session.add(user)
    session.commit()
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert_rejected(session, signed({"sub": str(user.id), "exp": expired}))


def test_a_token_signed_with_another_key_is_a_401(session):
    forged = jwt.encode({"sub": "x", "exp": in_one_hour()}, "some-other-secret", algorithm=settings.algorithm)
    assert_rejected(session, forged)


def test_garbage_is_a_401(session):
    assert_rejected(session, "this.is.not-a-token")    