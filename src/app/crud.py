from sqlalchemy.orm import Session
from src.app import models, schemas


def create_appointment(db: Session, data: schemas.AppointmentCreate) -> models.Appointment:
    appointment = models.Appointment(
        name=data.name,
        phone_number=data.phoneNumber,
        barber_id=data.barberId,
        service_id=data.serviceId,
        total_duration=data.totalDuration,
        total_price=data.totalPrice,
    )

    if data.addonIds:
        addons = db.query(models.Addon).filter(models.Addon.id.in_(data.addonIds)).all()
        appointment.addons = addons

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment_by_barber(db: Session, barber_id: int) -> list[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.barber_id == barber_id).all()
