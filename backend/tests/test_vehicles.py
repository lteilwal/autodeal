import pytest

from app.models import Vehicle

VALID_VEHICLE = {
    "make": "Toyota",
    "model": "Corolla",
    "category": "Sedan",
    "price": 25000.50,
    "quantity": 5,
}


def test_create_vehicle_returns_201_with_created_vehicle(client):
    response = client.post("/api/vehicles", json=VALID_VEHICLE)

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data == {"id": data["id"], **VALID_VEHICLE}


def test_create_vehicle_persists_to_database(client, db_session):
    response = client.post("/api/vehicles", json=VALID_VEHICLE)

    vehicle = db_session.get(Vehicle, response.json()["id"])
    assert vehicle is not None
    assert vehicle.make == "Toyota"
    assert vehicle.model == "Corolla"
    assert vehicle.category == "Sedan"
    assert float(vehicle.price) == 25000.50
    assert vehicle.quantity == 5


def test_create_vehicle_assigns_unique_ids(client):
    first = client.post("/api/vehicles", json=VALID_VEHICLE)
    second = client.post("/api/vehicles", json=VALID_VEHICLE)

    assert first.json()["id"] != second.json()["id"]


@pytest.mark.parametrize("missing_field", ["make", "model", "category", "price", "quantity"])
def test_create_vehicle_missing_field_returns_422(client, missing_field):
    payload = {k: v for k, v in VALID_VEHICLE.items() if k != missing_field}

    response = client.post("/api/vehicles", json=payload)

    assert response.status_code == 422


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
def test_create_vehicle_invalid_value_returns_422(client, field, value):
    response = client.post("/api/vehicles", json={**VALID_VEHICLE, field: value})

    assert response.status_code == 422
