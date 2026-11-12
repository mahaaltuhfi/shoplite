"""Unit tests for the User Service. Run with:  pytest"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app  # noqa: E402


@pytest.fixture
def client():
    # Uses a temporary in-memory database, so tests never touch PostgreSQL
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    return app.test_client()


def register(client, email="maha@test.com"):
    return client.post("/users", json={"name": "Maha", "email": email, "password": "pass123"})


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_register_user(client):
    r = register(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body["email"] == "maha@test.com"
    assert "password_hash" not in body  # password must never be returned


def test_register_missing_fields(client):
    r = client.post("/users", json={"email": "x@test.com"})
    assert r.status_code == 400


def test_register_duplicate_email(client):
    register(client)
    r = register(client)
    assert r.status_code == 409


def test_login_success(client):
    register(client)
    r = client.post("/login", json={"email": "maha@test.com", "password": "pass123"})
    assert r.status_code == 200
    assert "token" in r.get_json()


def test_login_wrong_password(client):
    register(client)
    r = client.post("/login", json={"email": "maha@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_get_user(client):
    user_id = register(client).get_json()["id"]
    r = client.get(f"/users/{user_id}")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Maha"


def test_get_missing_user(client):
    r = client.get("/users/999")
    assert r.status_code == 404