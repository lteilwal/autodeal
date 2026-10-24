from sqlalchemy import select

from app.models import User

COROLLA = {"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 25000, "quantity": 2}
F150 = {"make": "Ford", "model": "F-150", "category": "Truck", "price": 45000, "quantity": 1}


def register_and_login(client, email, password):
    credentials = {"email": email, "password": password}
    assert client.post("/api/auth/register", json=credentials).status_code == 201
    response = client.post("/api/auth/login", json=credentials)
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_full_api_flow(anon_client, db_session):
    api = anon_client
    user = register_and_login(api, "buyer@example.com", "buyer-password")
    admin = register_and_login(api, "boss@example.com", "boss-password")
    # Admins are promoted outside the API; an existing token picks up the new role.
    db_session.scalars(select(User).where(User.email == "boss@example.com")).one().is_admin = True
    db_session.commit()

    assert api.get("/api/vehicles").status_code == 401

    # Create
    corolla = api.post("/api/vehicles", json=COROLLA, headers=user)
    assert corolla.status_code == 201
    corolla_id = corolla.json()["id"]
    f150 = api.post("/api/vehicles", json=F150, headers=admin)
    assert f150.status_code == 201
    f150_id = f150.json()["id"]

    # List and search
    assert [v["model"] for v in api.get("/api/vehicles", headers=user).json()] == ["Corolla", "F-150"]
    search = api.get("/api/vehicles/search", params={"make": "toyota"}, headers=user)
    assert [v["id"] for v in search.json()] == [corolla_id]
    search = api.get("/api/vehicles/search", params={"min_price": 40000}, headers=user)
    assert [v["id"] for v in search.json()] == [f150_id]

    # Update
    updated = api.put(f"/api/vehicles/{corolla_id}", json={**COROLLA, "price": 24000}, headers=user)
    assert updated.status_code == 200
    assert updated.json()["price"] == 24000

    # Purchase until sold out
    bought = api.post(f"/api/vehicles/{corolla_id}/purchase", json={"quantity": 2}, headers=user)
    assert bought.json()["quantity"] == 0
    sold_out = api.post(f"/api/vehicles/{corolla_id}/purchase", json={"quantity": 1}, headers=user)
    assert sold_out.status_code == 409

    # Restock is admin-only
    denied = api.post(f"/api/vehicles/{corolla_id}/restock", json={"quantity": 3}, headers=user)
    assert denied.status_code == 403
    restocked = api.post(f"/api/vehicles/{corolla_id}/restock", json={"quantity": 3}, headers=admin)
    assert restocked.json()["quantity"] == 3
    bought = api.post(f"/api/vehicles/{corolla_id}/purchase", json={"quantity": 1}, headers=user)
    assert bought.json()["quantity"] == 2

    # Delete is admin-only
    assert api.delete(f"/api/vehicles/{f150_id}", headers=user).status_code == 403
    assert api.delete(f"/api/vehicles/{f150_id}", headers=admin).status_code == 204

    remaining = api.get("/api/vehicles", headers=user).json()
    assert remaining == [{"id": corolla_id, **COROLLA, "price": 24000, "quantity": 2}]
