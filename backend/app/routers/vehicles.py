from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Vehicle
from app.schemas import VehicleCreate, VehicleRead, VehicleSearch

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    return db.scalars(select(Vehicle).order_by(Vehicle.id)).all()


@router.get("/search", response_model=list[VehicleRead])
def search_vehicles(
    filters: Annotated[VehicleSearch, Query()], db: Session = Depends(get_db)
):
    query = select(Vehicle).order_by(Vehicle.id)
    if filters.make:
        query = query.where(Vehicle.make.icontains(filters.make, autoescape=True))
    if filters.model:
        query = query.where(Vehicle.model.icontains(filters.model, autoescape=True))
    if filters.category:
        query = query.where(Vehicle.category.icontains(filters.category, autoescape=True))
    if filters.min_price is not None:
        query = query.where(Vehicle.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Vehicle.price <= filters.max_price)
    return db.scalars(query).all()
