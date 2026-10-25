from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import select

from app.auth import ALGORITHM, SECRET_KEY, create_access_token, hash_password, verify_password
from app.models import User

from conftest import TEST_PASSWORD

NEW_USER = {"email": "new@example.com", "password": "s3cure-password"}

VEHICLE = {"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 25000, "quantity": 5}


def find_user(db_session, email):
    return db_session.scalars(select(User).where(User.email == email)).one_or_none()


# Password hashing


def test_hash_password_does_not_return_plain_text():
    assert hash_password("s3cure-password") != "s3cure-password"


def test_hash_password_is_salted():
    assert hash_password("s3cure-password") != hash_password("s3cure-password")


def test_verify_password_accepts_correct_and_rejects_wrong_password():
    hashed = hash_password("s3cure-password")

    assert verify_password("s3cure-password", hashed)
    assert not verify_password("wrong-password", hashed)


# POST /api/auth/register


def test_register_returns_201_with_user_and_no_password(anon_client):
    response = anon_client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 201
    data = response.json()
    assert data == {"id": data["id"], "email": "new@example.com", "is_admin": False}


def test_register_stores_hashed_password(anon_client, db_session):
    anon_client.post("/api/auth/register", json=NEW_USER)

    stored = find_user(db_session, "new@example.com")
    assert stored is not None
    assert stored.hashed_password != NEW_USER["password"]
    assert verify_password(NEW_USER["password"], stored.hashed_password)


def test_register_cannot_grant_admin(anon_client, db_session):
    response = anon_client.post("/api/auth/register", json={**NEW_USER, "is_admin": True})

    assert response.status_code == 201
    assert response.json()["is_admin"] is False
    assert find_user(db_session, "new@example.com").is_admin is False


def test_register_duplicate_email_returns_409(anon_client, db_session):
    anon_client.post("/api/auth/register", json=NEW_USER)

    response = anon_client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}
    assert len(db_session.scalars(select(User)).all()) == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "password": "s3cure-password"},
        {"email": "new@example.com", "password": "short"},
        {"email": "new@example.com"},
        {"password": "s3cure-password"},
    ],
)
def test_register_invalid_input_returns_422(anon_client, db_session, payload):
    response = anon_client.post("/api/auth/register", json=payload)

    assert response.status_code == 422
    assert db_session.scalars(select(User)).all() == []


# POST /api/auth/login


def test_login_returns_bearer_token_for_user(anon_client, user):
    response = anon_client.post(
        "/api/auth/login", json={"email": user.email, "password": TEST_PASSWORD}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(user.id)


def test_registered_user_can_log_in_and_use_token(anon_client):
    anon_client.post("/api/auth/register", json=NEW_USER)
    token = anon_client.post("/api/auth/login", json=NEW_USER).json()["access_token"]

    response = anon_client.get("/api/vehicles", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


@pytest.mark.parametrize(
    "credentials",
    [
        {"email": "user@example.com", "password": "wrong-password"},
        {"email": "nobody@example.com", "password": TEST_PASSWORD},
    ],
)
def test_login_with_incorrect_credentials_returns_401(anon_client, user, credentials):
    response = anon_client.post("/api/auth/login", json=credentials)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


# Protected vehicle routes

PROTECTED_ROUTES = [
    ("post", "/api/vehicles"),
    ("get", "/api/vehicles"),
    ("get", "/api/vehicles/search"),
    ("put", "/api/vehicles/1"),
    ("delete", "/api/vehicles/1"),
]


@pytest.mark.parametrize("method, path", PROTECTED_ROUTES)
def test_protected_routes_without_token_return_401(anon_client, method, path):
    kwargs = {"json": VEHICLE} if method in ("post", "put") else {}

    response = anon_client.request(method, path, **kwargs)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def expired_token(user):
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    return jwt.encode({"sub": str(user.id), "exp": expired}, SECRET_KEY, algorithm=ALGORITHM)


def wrong_secret_token(user):
    return jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "not-the-real-secret-key-for-this-app",
        algorithm=ALGORITHM,
    )


@pytest.mark.parametrize(
    "make_header",
    [
        lambda user: "Bearer not-a-jwt",
        lambda user: f"Bearer {expired_token(user)}",
        lambda user: f"Bearer {wrong_secret_token(user)}",
        lambda user: f"Bearer {create_access_token(user.id + 1000)}",
        lambda user: f"Basic {create_access_token(user.id)}",
    ],
    ids=["garbage", "expired", "wrong-secret", "unknown-user", "wrong-scheme"],
)
def test_invalid_token_returns_401(anon_client, user, make_header):
    response = anon_client.get("/api/vehicles", headers={"Authorization": make_header(user)})

    assert response.status_code == 401


def test_regular_user_can_access_protected_route(client):
    assert client.get("/api/vehicles").status_code == 200


def test_regular_user_cannot_access_admin_route(client, db_session):
    response = client.delete("/api/vehicles/1")

    assert response.status_code == 403


def test_health_does_not_require_token(anon_client):
    assert anon_client.get("/health").status_code == 200


# bcrypt only accepts up to 72 bytes; multi-byte characters reach that limit sooner.


def test_register_password_over_72_bytes_returns_422(anon_client, db_session):
    payload = {"email": "new@example.com", "password": "é" * 40}  # 40 chars, 80 bytes

    response = anon_client.post("/api/auth/register", json=payload)

    assert response.status_code == 422
    assert db_session.scalars(select(User)).all() == []


def test_login_with_overlong_password_returns_401(anon_client, user):
    response = anon_client.post(
        "/api/auth/login", json={"email": user.email, "password": "x" * 100}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


# GET /api/auth/me


def test_me_returns_regular_user(client, user):
    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"id": user.id, "email": "user@example.com", "is_admin": False}


def test_me_returns_admin_flag_for_admin(admin_client, admin):
    response = admin_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"id": admin.id, "email": "admin@example.com", "is_admin": True}


def test_me_without_token_returns_401(anon_client):
    response = anon_client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(anon_client):
    response = anon_client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401
