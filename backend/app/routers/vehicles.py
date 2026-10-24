from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import Vehicle
from app.schemas import StockChange, VehicleCreate, VehicleRead, VehicleSearch

router = APIRouter(
    prefix="/api/vehicles",
    tags=["vehicles"],
    dependencies=[Depends(get_current_user)],
)


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


def get_vehicle_or_404(db: Session, vehicle_id: int, for_update: bool = False) -> Vehicle:
    # for_update locks the row until commit so concurrent stock changes can't interleave.
    vehicle = db.get(Vehicle, vehicle_id, with_for_update=for_update or None)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(vehicle_id: int, payload: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db, vehicle_id)
    for field, value in payload.model_dump().items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db, vehicle_id)
    db.delete(vehicle)
    db.commit()


@router.post("/{vehicle_id}/purchase", response_model=VehicleRead)
def purchase_vehicle(vehicle_id: int, payload: StockChange, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db, vehicle_id, for_update=True)
    if vehicle.quantity < payload.quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock")
    vehicle.quantity -= payload.quantity
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.post(
    "/{vehicle_id}/restock",
    response_model=VehicleRead,
    dependencies=[Depends(require_admin)],
)
def restock_vehicle(vehicle_id: int, payload: StockChange, db: Session = Depends(get_db)):
    vehicle = get_vehicle_or_404(db, vehicle_id, for_update=True)
    vehicle.quantity += payload.quantity
    db.commit()
    db.refresh(vehicle)
    return vehicle
