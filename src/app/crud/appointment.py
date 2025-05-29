from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.models.appointment import Appointment, Addon
from src.app.models.service import Service
from src.app.schemas.appointment import AppointmentCreate


def create_appointment(db: Session, data: AppointmentCreate):
    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=400, detail="Service not found")

    addons = db.query(Addon).filter(Addon.id.in_(data.addon_ids)).all()

    total_price = service.price + sum(addon.price for addon in addons)
    total_duration = service.duration + sum(addon.duration for addon in addons)

    if len(addons) != len(data.addon_ids):
        raise HTTPException(status_code=400, detail="Some addon IDs not found")

    appointment = Appointment(
        name=data.name,
        phone_number=data.phone_number,
        barber_id=data.barber_id,
        service_id=data.service_id,
        total_duration=total_duration,
        total_price=total_price,
        addons=addons,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment_by_barber(db: Session, barber_id: int) -> List[Appointment]:
    return db.query(Appointment).filter(Appointment.barber_id == barber_id).all()


def delete_appointment(db: Session, appointment_id: int) -> bool:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return False

    db.delete(appointment)
    db.commit()
    return True
