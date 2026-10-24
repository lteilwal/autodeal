import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Vehicle


@pytest.fixture
def vehicle(db_session):
    vehicle = Vehicle(make="Toyota", model="Corolla", category="Sedan", price=25000, quantity=5)
    db_session.add(vehicle)
    db_session.commit()
    return vehicle


@pytest.fixture
def sold_out_vehicle(db_session):
    vehicle = Vehicle(make="Honda", model="Civic", category="Sedan", price=23000, quantity=0)
    db_session.add(vehicle)
    db_session.commit()
    return vehicle


def stored_quantity(db_session, vehicle_id):
    # Drop cached objects so the next read comes from PostgreSQL.
    db_session.expire_all()
    return db_session.get(Vehicle, vehicle_id).quantity


INVALID_QUANTITIES = [
    {"quantity": 0},
    {"quantity": -1},
    {"quantity": 1.5},
    {"quantity": "two"},
    {},
]


# POST /api/vehicles/{id}/purchase


def test_purchase_decreases_quantity(client, db_session, vehicle):
    response = client.post(f"/api/vehicles/{vehicle.id}/purchase", json={"quantity": 2})

    assert response.status_code == 200
    assert response.json()["id"] == vehicle.id
    assert response.json()["quantity"] == 3
    assert stored_quantity(db_session, vehicle.id) == 3


def test_purchase_entire_stock_leaves_zero(client, db_session, vehicle):
    response = client.post(f"/api/vehicles/{vehicle.id}/purchase", json={"quantity": 5})

    assert response.status_code == 200
    assert stored_quantity(db_session, vehicle.id) == 0


def test_purchase_sold_out_vehicle_returns_409(client, db_session, sold_out_vehicle):
    response = client.post(f"/api/vehicles/{sold_out_vehicle.id}/purchase", json={"quantity": 1})

    assert response.status_code == 409
    assert response.json() == {"detail": "Insufficient stock"}
    assert stored_quantity(db_session, sold_out_vehicle.id) == 0


def test_purchase_more_than_in_stock_returns_409(client, db_session, vehicle):
    response = client.post(f"/api/vehicles/{vehicle.id}/purchase", json={"quantity": 6})

    assert response.status_code == 409
    assert response.json() == {"detail": "Insufficient stock"}
    assert stored_quantity(db_session, vehicle.id) == 5


@pytest.mark.parametrize("payload", INVALID_QUANTITIES)
def test_purchase_invalid_quantity_returns_422(client, db_session, vehicle, payload):
    response = client.post(f"/api/vehicles/{vehicle.id}/purchase", json=payload)

    assert response.status_code == 422
    assert stored_quantity(db_session, vehicle.id) == 5


def test_purchase_missing_vehicle_returns_404(client):
    response = client.post("/api/vehicles/999999/purchase", json={"quantity": 1})

    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}


def test_admin_can_purchase(admin_client, db_session, vehicle):
    response = admin_client.post(f"/api/vehicles/{vehicle.id}/purchase", json={"quantity": 1})

    assert response.status_code == 200
    assert stored_quantity(db_session, vehicle.id) == 4


def test_unauthenticated_purchase_returns_401(anon_client, db_session, vehicle):
    response = anon_client.post(f"/api/vehicles/{vehicle.id}/purchase", json={"quantity": 1})

    assert response.status_code == 401
    assert stored_quantity(db_session, vehicle.id) == 5


# POST /api/vehicles/{id}/restock


def test_admin_restock_increases_quantity(admin_client, db_session, vehicle):
    response = admin_client.post(f"/api/vehicles/{vehicle.id}/restock", json={"quantity": 10})

    assert response.status_code == 200
    assert response.json()["id"] == vehicle.id
    assert response.json()["quantity"] == 15
    assert stored_quantity(db_session, vehicle.id) == 15


def test_admin_can_restock_sold_out_vehicle(admin_client, db_session, sold_out_vehicle):
    response = admin_client.post(
        f"/api/vehicles/{sold_out_vehicle.id}/restock", json={"quantity": 3}
    )

    assert response.status_code == 200
    assert stored_quantity(db_session, sold_out_vehicle.id) == 3


@pytest.mark.parametrize("payload", INVALID_QUANTITIES)
def test_restock_invalid_quantity_returns_422(admin_client, db_session, vehicle, payload):
    response = admin_client.post(f"/api/vehicles/{vehicle.id}/restock", json=payload)

    assert response.status_code == 422
    assert stored_quantity(db_session, vehicle.id) == 5


def test_restock_missing_vehicle_returns_404(admin_client):
    response = admin_client.post("/api/vehicles/999999/restock", json={"quantity": 1})

    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}


def test_regular_user_cannot_restock(client, db_session, vehicle):
    response = client.post(f"/api/vehicles/{vehicle.id}/restock", json={"quantity": 10})

    assert response.status_code == 403
    assert stored_quantity(db_session, vehicle.id) == 5


def test_unauthenticated_restock_returns_401(anon_client, db_session, vehicle):
    response = anon_client.post(f"/api/vehicles/{vehicle.id}/restock", json={"quantity": 10})

    assert response.status_code == 401
    assert stored_quantity(db_session, vehicle.id) == 5


# Database safety net


def test_database_rejects_negative_quantity(db_session, vehicle):
    vehicle.quantity = -1

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
