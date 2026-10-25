"""Insert sample cars into the database configured by DATABASE_URL.

Run from the backend/ folder:  ../.venv/Scripts/python seed_vehicles.py

Safe to rerun: a sample is skipped when a vehicle with the same make, model and
category already exists, and existing rows are never updated or deleted.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import Vehicle

SAMPLE_VEHICLES = [
    {"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22050, "quantity": 7},
    {"make": "Toyota", "model": "RAV4", "category": "SUV", "price": 29800, "quantity": 4},
    {"make": "Honda", "model": "Civic", "category": "Sedan", "price": 24250, "quantity": 0},
    {"make": "Honda", "model": "CR-V", "category": "SUV", "price": 30850, "quantity": 3},
    {"make": "Ford", "model": "F-150", "category": "Truck", "price": 38810, "quantity": 5},
    {"make": "Ford", "model": "Mustang", "category": "Coupe", "price": 31920, "quantity": 2},
    {"make": "Chevrolet", "model": "Silverado 1500", "category": "Truck", "price": 37645, "quantity": 0},
    {"make": "Tesla", "model": "Model 3", "category": "Electric", "price": 38990, "quantity": 6},
    {"make": "BMW", "model": "3 Series", "category": "Sedan", "price": 45500, "quantity": 2},
    {"make": "Mazda", "model": "MX-5 Miata", "category": "Convertible", "price": 29930, "quantity": 1},
    {"make": "Subaru", "model": "Outback", "category": "Wagon", "price": 29995, "quantity": 0},
    {"make": "Hyundai", "model": "Ioniq 5", "category": "Electric", "price": 42600, "quantity": 3},
]


def seed_vehicles(session: Session) -> int:
    """Add any missing sample vehicles and return how many were inserted."""
    existing = {
        tuple(row) for row in session.execute(select(Vehicle.make, Vehicle.model, Vehicle.category))
    }
    new = [
        Vehicle(**sample)
        for sample in SAMPLE_VEHICLES
        if (sample["make"], sample["model"], sample["category"]) not in existing
    ]
    session.add_all(new)
    session.commit()
    return len(new)


if __name__ == "__main__":
    init_db()
    with SessionLocal() as session:
        inserted = seed_vehicles(session)
    skipped = len(SAMPLE_VEHICLES) - inserted
    print(f"Inserted {inserted} sample vehicles ({skipped} already present).")
