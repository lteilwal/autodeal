from sqlalchemy import inspect, select

from app import main as main_module
from app.database import Base, engine as app_engine, init_db
from app.main import app
from app.models import User, Vehicle
from fastapi.testclient import TestClient

FRONTEND_ORIGIN = "http://localhost:5173"


# Database initialization


def test_init_db_creates_tables_with_constraints(engine):
    with engine.connect() as connection:
        # PostgreSQL DDL is transactional, so dropping here is undone by the rollback.
        transaction = connection.begin()
        Base.metadata.drop_all(connection)

        init_db(connection)

        inspector = inspect(connection)
        assert {"users", "vehicles"} <= set(inspector.get_table_names())
        checks = {c["name"] for c in inspector.get_check_constraints("vehicles")}
        assert "vehicle_quantity_non_negative" in checks
        unique_columns = [c["column_names"] for c in inspector.get_unique_constraints("users")]
        assert ["email"] in unique_columns
        transaction.rollback()


def test_init_db_keeps_existing_data(db_session):
    db_session.add(Vehicle(make="Toyota", model="Corolla", category="Sedan", price=1, quantity=1))
    db_session.add(User(email="keep@example.com", hashed_password="x"))
    db_session.commit()

    init_db(db_session.connection())
    init_db(db_session.connection())

    db_session.expire_all()
    assert db_session.scalars(select(Vehicle.model)).all() == ["Corolla"]
    assert db_session.scalars(select(User.email)).all() == ["keep@example.com"]


def test_app_startup_initializes_database(monkeypatch):
    calls = []
    monkeypatch.setattr(main_module, "init_db", calls.append)

    with TestClient(app):
        pass

    assert calls == [app_engine]


# CORS for the React dev server


def test_cors_preflight_allows_frontend_origin_with_auth_header():
    response = TestClient(app).options(
        "/api/vehicles",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "authorization" in allowed_headers


def test_cors_rejects_unknown_origin():
    response = TestClient(app).get("/health", headers={"Origin": "http://evil.example.com"})

    assert "access-control-allow-origin" not in response.headers
