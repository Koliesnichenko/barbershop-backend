from typing import List, Union, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.models.addon import Addon
from src.app.models.barber import Barber
from src.app.models.service import Service
from src.app.schemas.barber import BarberCreate, BarberBase, BarberUpdate


def create_barber(db: Session, barber: BarberCreate):
    new_barber = Barber(**barber.model_dump())
    db.add(new_barber)
    db.commit()
    db.refresh(new_barber)
    return new_barber


def get_barbers(db: Session):
    return db.query(Barber).all()


def get_barber(db: Session, barber_id: int):
    return db.query(Barber).filter(Barber.id == barber_id).first()


def update_barber(db: Session, barber_id: int, updated_data: BarberUpdate):
    barber = get_barber(db, barber_id)
    if barber:
        for key, value in updated_data.model_dump().items():
            setattr(barber, key, value)
        db.commit()
        db.refresh(barber)
    return barber


def delete_barber(db: Session, barber_id: int):
    barber = get_barber(db, barber_id)
    if barber:
        db.delete(barber)
        db.commit()
        return True
    return False


def assign_services_to_barber(db: Session, barber_id: int, service_ids: List[int]):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        return None

    existing_ids = {service.id for service in barber.services}
    new_ids = set(service_ids) - existing_ids

    if not new_ids:
        return barber

    new_services = db.query(Service).filter(Service.id.in_(new_ids)).all()
    if len(new_services) != len(new_ids):
        raise HTTPException(status_code=400, detail="Some service IDs were not found")

    barber.services.extend(new_services)

    db.commit()
    db.refresh(barber)
    return barber


def assign_addons_to_barber(db: Session, barber_id: int, addon_ids: List[int]):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        return None

    existing_ids = {addon.id for addon in barber.addons}
    new_ids = set(addon_ids) - existing_ids

    if not new_ids:
        return barber

    new_addons = db.query(Addon).filter(Addon.id.in_(new_ids)).all()

    if len(new_addons) != len(new_ids):
        raise HTTPException(status_code=400, detail="Some addon IDs were not found")

    barber.addons.extend(new_addons)

    db.commit()
    db.refresh(barber)
    return barber


def remove_service_from_barber(db: Session, barber_id: int, service_id: int) -> Optional[Barber]:
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        return None

    service = next((service for service in barber.services if service.id == service_id), None)
    if not service:
        raise HTTPException(status_code=400, detail="Service not assigned to this barber")

    barber.services.remove(service)
    db.commit()
    db.refresh(barber)
    return barber


def remove_addon_from_barber(db: Session, barber_id: int, addon_id: int) -> Optional[Barber]:
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        return None

    addon = next((addon for addon in barber.addons if addon.id == addon_id), None)
    if not addon:
        raise HTTPException(status_code=400, detail="Addon not assigned to this barber")

    barber.addons.remove(addon)
    db.commit()
    db.refresh(barber)
    return barber
