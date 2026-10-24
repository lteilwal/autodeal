import pytest

from app.models import Vehicle

UPDATED_VEHICLE = {
    "make": "Honda",
    "model": "Accord",
    "category": "Coupe",
    "price": 31000.75,
    "quantity": 8,
}


@pytest.fixture
def vehicle(db_session):
    vehicle = Vehicle(make="Toyota", model="Corolla", category="Sedan", price=25000, quantity=5)
    db_session.add(vehicle)
    db_session.commit()
    return vehicle


def reload(db_session, vehicle_id):
    # Drop cached objects so the next read comes from PostgreSQL.
    db_session.expire_all()
    return db_session.get(Vehicle, vehicle_id)


# PUT /api/vehicles/{id}


def test_update_vehicle_returns_200_with_updated_vehicle(client, vehicle):
    response = client.put(f"/api/vehicles/{vehicle.id}", json=UPDATED_VEHICLE)

    assert response.status_code == 200
    assert response.json() == {"id": vehicle.id, **UPDATED_VEHICLE}


def test_update_vehicle_persists_to_database(client, db_session, vehicle):
    client.put(f"/api/vehicles/{vehicle.id}", json=UPDATED_VEHICLE)

    stored = reload(db_session, vehicle.id)
    assert stored.make == "Honda"
    assert stored.model == "Accord"
    assert stored.category == "Coupe"
    assert float(stored.price) == 31000.75
    assert stored.quantity == 8


def test_update_missing_vehicle_returns_404(client):
    response = client.put("/api/vehicles/999999", json=UPDATED_VEHICLE)

    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}


@pytest.mark.parametrize(
    "field, value",
    [
        ("make", ""),
        ("model", ""),
        ("category", ""),
        ("price", 0),
        ("price", -1),
        ("quantity", -1),
        ("quantity", 1.5),
    ],
)
def test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged(
    client, db_session, vehicle, field, value
):
    response = client.put(f"/api/vehicles/{vehicle.id}", json={**UPDATED_VEHICLE, field: value})

    assert response.status_code == 422
    stored = reload(db_session, vehicle.id)
    assert stored.make == "Toyota"
    assert stored.quantity == 5


@pytest.mark.parametrize("missing_field", ["make", "model", "category", "price", "quantity"])
def test_update_with_missing_field_returns_422(client, vehicle, missing_field):
    payload = {k: v for k, v in UPDATED_VEHICLE.items() if k != missing_field}

    response = client.put(f"/api/vehicles/{vehicle.id}", json=payload)

    assert response.status_code == 422


# DELETE /api/vehicles/{id}


def test_admin_can_delete_vehicle(admin_client, db_session, vehicle):
    vehicle_id = vehicle.id

    response = admin_client.delete(f"/api/vehicles/{vehicle_id}")

    assert response.status_code == 204
    assert reload(db_session, vehicle_id) is None


def test_deleted_vehicle_no_longer_listed_or_deletable(admin_client, vehicle):
    vehicle_id = vehicle.id
    admin_client.delete(f"/api/vehicles/{vehicle_id}")

    assert admin_client.get("/api/vehicles").json() == []
    response = admin_client.delete(f"/api/vehicles/{vehicle_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}


def test_delete_missing_vehicle_returns_404(admin_client):
    response = admin_client.delete("/api/vehicles/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}


def test_non_admin_cannot_delete_vehicle(client, db_session, vehicle):
    response = client.delete(f"/api/vehicles/{vehicle.id}")

    assert response.status_code == 403
    assert reload(db_session, vehicle.id) is not None


def test_unauthenticated_user_cannot_delete_vehicle(anon_client, db_session, vehicle):
    response = anon_client.delete(f"/api/vehicles/{vehicle.id}")

    assert response.status_code == 401
    assert reload(db_session, vehicle.id) is not None
