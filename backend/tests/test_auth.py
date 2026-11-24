import pytest
from app.auth import hash_password, verify_password, create_access_token, _decode_token
from app.models.auth import User


def test_password_hashing():
    pw = "SuperSecurePass123!"
    hashed = hash_password(pw)
    assert hashed.startswith("scrypt$")
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_token_creation_and_decoding():
    user = User(email="test@user.com", role="admin", id=99, status="active")
    token = create_access_token(user)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    claims = _decode_token(token)
    assert claims["sub"] == 99
    assert claims["role"] == "admin"
    assert "exp" in claims


def test_unauthenticated_request_rejected(client):
    res = client.get("/api/admin/dashboard/summary")
    assert res.status_code == 401
    assert "detail" in res.json()


def test_forbidden_role_access(client, customer_headers):
    # Customer trying to access Admin dashboard endpoint
    res = client.get("/api/admin/dashboard/summary", headers=customer_headers)
    assert res.status_code == 403
    assert "permission" in res.json()["detail"].lower()


def test_valid_admin_login(client):
    payload = {
        "identifier": "admin@moderncolours.local",
        "password": "AdminPass123!",
        "role": "admin",
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["token_type"] == "bearer"
