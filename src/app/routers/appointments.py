from datetime import datetime, timedelta, UTC, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.app import crud
from src.app.auth.dependencies import get_current_user, admin_required
from src.app.database import get_db
from src.app.crud.appointment import create_appointment as create_appointment_crud, get_appointment_by_barber

from typing import List

from src.app.models.appointment import Appointment, AppointmentStatus
from src.app.models.barber import Barber
from src.app.models.service import Service
from src.app.models.user import User
from src.app.schemas.appointment import AppointmentCreate, AppointmentReadDetailed, AppointmentResponse, \
    AppointmentShortUserView, AddonsOut

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
        appointment: AppointmentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    created_appointment = create_appointment_crud(db=db, data=appointment, user_id=current_user.id)

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
