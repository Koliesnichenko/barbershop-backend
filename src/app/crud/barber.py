from typing import List

from sqlalchemy.orm import Session

from src.app.models.barber import Barber
from src.app.models.service import Service
from src.app.schemas.barber import BarberCreate, BarberBase


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


def update_barber(db: Session, barber_id: int, updated_data: BarberBase):
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


def assign_services_to_barber(db: Session, barber_id: int, service_id: List[int]):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        return None
    services = db.query(Service).filter(Service.id.in_(service_id)).all()
    barber.services = services
    db.commit()
    db.refresh(barber)
    return barber


