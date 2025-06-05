from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.dependencies import admin_required, get_current_user
from src.app.database import get_db
from src.app.crud import barber as crud
from src.app.models.user import User
from src.app.schemas.barber import BarberCreate, BarberRead, BarberBase, AssignServices, BarberUpdate, AssignAddons
from typing import List

router = APIRouter(tags=["Barbers"])


@router.post("/", response_model=BarberRead)
def create_barber(
        barber: BarberCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    return crud.create_barber(db=db, barber=barber)


@router.get("/", response_model=List[BarberRead])
def get_all_barbers(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud.get_barbers(db=db)


@router.put("/{barber_id}", response_model=BarberRead)
def update_barber(
        barber_id: int,
        updated_data: BarberUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    result = crud.update_barber(db=db, barber_id=barber_id, updated_data=updated_data)
    if not result:
        raise HTTPException(status_code=404, detail="Barber not found")
    return result


@router.delete("/{barber_id}", status_code=204)
def delete_barber(
        barber_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    if not crud.delete_barber(db=db, barber_id=barber_id):
        raise HTTPException(status_code=404, detail="Barber not found")


@router.post("/{barber_id}/service", response_model=BarberRead)
def assign_services(
        barber_id: int,
        payload: AssignServices,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    result = crud.assign_services_to_barber(db, barber_id, payload.service_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Barber not found or invalid service IDs")
    return result


@router.post("/{barber_id}/addon", response_model=BarberRead)
def assign_addons(
        barber_id: int,
        payload: AssignAddons,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    result = crud.assign_addons_to_barber(db, barber_id, payload.addon_ids)
    if not result:
        raise HTTPException(status_code=404, detail="Barber not found or invalid addon IDs")
    return result


@router.delete("/{barber_id}/service/{service_id}", response_model=BarberRead)
def remove_service(
        barber_id: int,
        service_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    result = crud.remove_service_from_barber(db, barber_id, service_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Invalid service IDs")
    return result


@router.delete("/{barber_id}/addon/{addon_id}", response_model=BarberRead)
def remove_addon(
        barber_id: int,
        addon_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    result = crud.remove_addon_from_barber(db, barber_id, addon_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Invalid addon IDs")
    return result
