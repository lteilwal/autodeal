from sqlalchemy import func, select

from app.models import Vehicle
from seed_vehicles import SAMPLE_VEHICLES, seed_vehicles


def all_vehicles(db_session):
    db_session.expire_all()
    return db_session.scalars(select(Vehicle).order_by(Vehicle.id)).all()


def test_sample_data_is_varied_and_includes_sold_out_cars():
    assert len(SAMPLE_VEHICLES) == 12
    assert len({v["make"] for v in SAMPLE_VEHICLES}) >= 6
    assert len({v["category"] for v in SAMPLE_VEHICLES}) >= 4
    assert any(v["quantity"] == 0 for v in SAMPLE_VEHICLES)
    assert all("id" not in v for v in SAMPLE_VEHICLES)


def test_seed_inserts_all_samples_with_generated_ids(db_session):
    inserted = seed_vehicles(db_session)

    vehicles = all_vehicles(db_session)
    assert inserted == 12
    assert len(vehicles) == 12
    assert all(isinstance(v.id, int) for v in vehicles)
    assert len({v.id for v in vehicles}) == 12


def test_rerunning_seed_does_not_duplicate(db_session):
    seed_vehicles(db_session)

    inserted_again = seed_vehicles(db_session)

    assert inserted_again == 0
    assert db_session.scalar(select(func.count()).select_from(Vehicle)) == 12


def test_seed_keeps_existing_inventory_untouched(db_session):
    sample = SAMPLE_VEHICLES[0]
    # Same car as a sample, but with the dealer's own price and stock.
    existing = Vehicle(**{**sample, "price": 1, "quantity": 99})
    unrelated = Vehicle(make="Lada", model="Niva", category="SUV", price=9000, quantity=4)
    db_session.add_all([existing, unrelated])
    db_session.commit()

    inserted = seed_vehicles(db_session)

    assert inserted == 11
    vehicles = all_vehicles(db_session)
    assert len(vehicles) == 13
    kept = db_session.get(Vehicle, existing.id)
    assert (float(kept.price), kept.quantity) == (1.0, 99)
    lada = db_session.get(Vehicle, unrelated.id)
    assert (lada.make, lada.model, float(lada.price), lada.quantity) == ("Lada", "Niva", 9000.0, 4)
