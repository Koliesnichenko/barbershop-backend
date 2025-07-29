import logging
from datetime import datetime, timedelta, UTC, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.app import crud
from src.app.auth.dependencies import get_current_user, admin_required
from src.app.core.config import settings
from src.app.database import get_db
from src.app.crud.appointment import get_appointment_by_barber
from src.app.tasks.email import send_email

from typing import List

from src.app.models.appointment import Appointment, AppointmentStatus
from src.app.models.barber import Barber
from src.app.models.service import Service
from src.app.models.user import User
from src.app.schemas.appointment import AppointmentCreate, AppointmentReadDetailed, AppointmentResponse, \
    AppointmentShortUserView, AddonsOut
from src.app.services.email_service import send_booking_confirmation_email, send_booking_cancellation_email
from src.app.services.timeslot_generator import create_appointment_with_checks

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
        appointment: AppointmentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    created_appointment = create_appointment_with_checks(
        db=db,
        data=appointment,
        user_id=current_user.id
    )

    scheduled_datetime = created_appointment.scheduled_time

    if scheduled_datetime.tzinfo is None:
        scheduled_datetime = scheduled_datetime.replace(tzinfo=timezone.utc)

    scheduled_day = scheduled_datetime.strftime("%A")
    scheduled_date = scheduled_datetime.strftime("%Y-%m-%d")
    scheduled_time_str = scheduled_datetime.strftime("%H:%M")

    send_booking_confirmation_email(
        email_to=current_user.email,
        user_name=current_user.name,
        scheduled_day=scheduled_day,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time_str,
        barber_name=created_appointment.barber.name,
        service_title=AppointmentResponse.model_validate(created_appointment).full_service_title,
        total_price=created_appointment.total_price,
        total_duration=created_appointment.total_duration,
        status=created_appointment.status.value,
        frontend_url=settings.FRONTEND_URL
    )

    reminder = scheduled_datetime - timedelta(minutes=10)

    if reminder > datetime.now(timezone.utc):
        send_reminder_email.apply_async(
            args=[
                current_user.email,
                "Upcoming appointment reminder",
                f"Hi {current_user.name}!, this is reminder about your appointment at {scheduled_time_str}."
            ],
            eta=reminder
        )
        logger.info(f"Scheduled reminder email for appointment ID {created_appointment.id} at {reminder}.")
    else:
        logger.warning(f"Reminder time ({reminder}) for appointment ID {created_appointment.id} "
                       f"already passed ({datetime.now(timezone.utc)}), skipping scheduling reminder email.")

    logger.info(f"API: Appointment ID {created_appointment.id} successfully processed for user {current_user.id}.")
    return created_appointment


@router.get("/barber/{barber_id}", response_model=List[AppointmentResponse])
def get_appointments_by_barber(
        barber_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    try:
        appointments_from_db = get_appointment_by_barber(db, barber_id)
        return appointments_from_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
        appointment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can't delete this appointment")

    if appointment.status == AppointmentStatus.cancelled:
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")

    appointment.status = AppointmentStatus.cancelled
    db.commit()
    db.refresh(appointment)

    scheduled_datetime = appointment.scheduled_time
    scheduled_day = scheduled_datetime.strftime("%A")
    scheduled_date = scheduled_datetime.strftime("%Y-%m-%d")
    scheduled_time = scheduled_datetime.strftime("%H:%M")

    send_booking_cancellation_email(
        email_to=current_user.email,
        user_name=current_user.name,
        scheduled_day=scheduled_day,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        barber_name=appointment.barber.name,
        service_title=AppointmentResponse.model_validate(appointment).full_service_title,
        total_price=appointment.total_price,
        total_duration=appointment.total_duration,
        status=appointment.status.value,
        frontend_url=settings.FRONTEND_URL
    )

    return {"message": "Appointment cancelled successfully", "status": appointment.status}


@router.post("/{appointment_id}/complete", status_code=status.HTTP_200_OK)
def complete_appointment(
        appointment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status == AppointmentStatus.completed:
        raise HTTPException(status_code=400, detail="Appointment is already completed")
    if appointment.status == AppointmentStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot complete a cancelled appointment")

    appointment.status = AppointmentStatus.completed
    db.commit()
    db.refresh(appointment)

    return {"message": "Appointment marked as completed", "status": appointment.status}


@router.get("/me", response_model=List[AppointmentShortUserView])
def get_user_appointments(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    now = datetime.now(timezone.utc)

    appointments = (
        db.query(Appointment)
        .filter(Appointment.user_id == current_user.id)
        .options(
            joinedload(Appointment.service),
            joinedload(Appointment.addons),
            joinedload(Appointment.barber)
        )
        .order_by(Appointment.scheduled_time.asc())
        .all()
    )

    def to_short_view(a: Appointment) -> AppointmentShortUserView:
        start = a.scheduled_time

        end = start + timedelta(minutes=a.total_duration)

        a.scheduled_time = a.scheduled_time.replace(tzinfo=timezone.utc)

        full_service_title = " + ".join([a.service.name] + [addon.name for addon in a.addons])

        return AppointmentShortUserView(
            id=a.id,
            barber_name=a.barber.name,
            full_service_title=full_service_title,
            scheduled_day=start.strftime("%A"),
            scheduled_date=start.strftime("%d.%m.%Y"),
            scheduled_time=f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
            total_price=a.total_price,
            status=a.status
        )

    return [to_short_view(a) for a in appointments]
