from sqlalchemy.orm import Session
from src.app import models, schemas


def create_appointment(db: Session, data: schemas.AppointmentCreate) -> models.Appointment:
    appointment = models.Appointment(
        name=data.name,
        phone_number=data.phone_number,
        barber_id=data.barber_id,
        service_id=data.service_id,
        total_duration=data.total_duration,
        total_price=data.total_price,
    )

    if data.addon_ids:
        addons = db.query(models.Addon).filter(models.Addon.id.in_(data.addon_ids)).all()
        appointment.addons = addons

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment_by_barber(db: Session, barber_id: int) -> list[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.barber_id == barber_id).all()


def delete_appointment(db: Session, appointment_id: int) -> bool:
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appointment:
        return False

    db.delete(appointment)
    db.commit()
    return True
