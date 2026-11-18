"""Tests for PATCH /users/me (change email). Run from backend/:  python -m pytest"""

PASSWORD = "correct-horse-battery"


def signup_and_login(client, email):
    assert client.post("/auth/signup", json={"email": email, "password": PASSWORD}).status_code == 201
    token = client.post("/auth/login", json={"email": email, "password": PASSWORD}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_change_email_with_correct_password(client):
    auth = signup_and_login(client, "old@example.com")
    res = client.patch("/users/me", headers=auth, json={"email": "new@example.com", "current_password": PASSWORD})
    assert res.status_code == 200
    assert res.json()["email"] == "new@example.com"
    assert client.get("/users/me", headers=auth).json()["email"] == "new@example.com"
    # the new email logs in, the old one no longer does -Arun
    assert client.post("/auth/login", json={"email": "new@example.com", "password": PASSWORD}).status_code == 200
    assert client.post("/auth/login", json={"email": "old@example.com", "password": PASSWORD}).status_code == 401


def test_wrong_or_missing_password_is_rejected(client):
    auth = signup_and_login(client, "old@example.com")
    for body in ({"email": "new@example.com", "current_password": "wrong-password-123"}, {"email": "new@example.com"}):
        res = client.patch("/users/me", headers=auth, json=body)
        assert res.status_code == 400
        assert res.json()["detail"] == "Current password is incorrect"
    assert client.get("/users/me", headers=auth).json()["email"] == "old@example.com"


def test_email_taken_by_someone_else(client):
    signup_and_login(client, "taken@example.com")
    auth = signup_and_login(client, "me@example.com")
    res = client.patch("/users/me", headers=auth, json={"email": "taken@example.com", "current_password": PASSWORD})
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already in use"


def test_same_email_needs_no_password(client):
    auth = signup_and_login(client, "me@example.com")
    res = client.patch("/users/me", headers=auth, json={"email": "me@example.com"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"


def test_invalid_email_is_422(client):
    auth = signup_and_login(client, "me@example.com")
    res = client.patch("/users/me", headers=auth, json={"email": "not-an-email", "current_password": PASSWORD})
    assert res.status_code == 422


def test_requires_login(client):
    res = client.patch("/users/me", json={"email": "new@example.com", "current_password": PASSWORD})
    assert res.status_code in (401, 403)
