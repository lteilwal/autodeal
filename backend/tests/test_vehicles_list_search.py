import pytest

from app.models import Vehicle


@pytest.fixture
def vehicles(db_session):
    vehicles = [
        Vehicle(make="Toyota", model="Corolla", category="Sedan", price=25000, quantity=5),
        Vehicle(make="Toyota", model="RAV4", category="SUV", price=32000, quantity=3),
        Vehicle(make="Honda", model="Civic", category="Sedan", price=23000, quantity=0),
        Vehicle(make="Ford", model="F-150", category="Truck", price=45000, quantity=2),
    ]
    db_session.add_all(vehicles)
    db_session.commit()
    return vehicles


def models_in(response):
    return [vehicle["model"] for vehicle in response.json()]


# GET /api/vehicles


def test_list_vehicles_empty_returns_empty_list(client):
    response = client.get("/api/vehicles")

    assert response.status_code == 200
    assert response.json() == []


def test_list_vehicles_returns_all_vehicles_ordered_by_id(client, vehicles):
    response = client.get("/api/vehicles")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": v.id,
            "make": v.make,
            "model": v.model,
            "category": v.category,
            "price": float(v.price),
            "quantity": v.quantity,
        }
        for v in vehicles
    ]


# GET /api/vehicles/search


@pytest.mark.parametrize(
    "params, expected_models",
    [
        ({"make": "toyota"}, ["Corolla", "RAV4"]),
        ({"model": "civ"}, ["Civic"]),
        ({"category": "SEDAN"}, ["Corolla", "Civic"]),
        ({"min_price": 30000}, ["RAV4", "F-150"]),
        ({"max_price": 25000}, ["Corolla", "Civic"]),
        ({"min_price": 23000, "max_price": 32000}, ["Corolla", "RAV4", "Civic"]),
    ],
)
def test_search_by_single_filter(client, vehicles, params, expected_models):
    response = client.get("/api/vehicles/search", params=params)

    assert response.status_code == 200
    assert models_in(response) == expected_models


def test_search_with_combined_filters_matches_all_of_them(client, vehicles):
    params = {"make": "toyota", "category": "suv", "max_price": 40000}

    response = client.get("/api/vehicles/search", params=params)

    assert response.status_code == 200
    assert models_in(response) == ["RAV4"]


def test_search_with_no_filters_returns_all_vehicles(client, vehicles):
    response = client.get("/api/vehicles/search")

    assert response.status_code == 200
    assert models_in(response) == ["Corolla", "RAV4", "Civic", "F-150"]


def test_search_with_no_matches_returns_empty_list(client, vehicles):
    response = client.get("/api/vehicles/search", params={"make": "Tesla"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_min_price_greater_than_max_price_returns_422(client, vehicles):
    params = {"min_price": 40000, "max_price": 20000}

    response = client.get("/api/vehicles/search", params=params)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "params",
    [
        {"min_price": -1},
        {"max_price": -1},
        {"min_price": "cheap"},
        {"max_price": "expensive"},
    ],
)
def test_search_invalid_price_returns_422(client, vehicles, params):
    response = client.get("/api/vehicles/search", params=params)

    assert response.status_code == 422
