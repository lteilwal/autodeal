import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models import User

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres@localhost:5432/car_inventory_test",
)

TEST_PASSWORD = "correct-horse-battery"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(engine):
    # Each test runs inside an outer transaction that is rolled back afterwards,
    # so commits made by app code never persist between tests.
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def password_hash():
    # Hash once per run; bcrypt is deliberately slow.
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def user(db_session, password_hash):
    user = User(email="user@example.com", hashed_password=password_hash, is_admin=False)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin(db_session, password_hash):
    admin = User(email="admin@example.com", hashed_password=password_hash, is_admin=True)
    db_session.add(admin)
    db_session.commit()
    return admin


def bearer(user):
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture
def anon_client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client(anon_client, user):
    return TestClient(app, headers=bearer(user))


@pytest.fixture
def admin_client(anon_client, admin):
    return TestClient(app, headers=bearer(admin))
