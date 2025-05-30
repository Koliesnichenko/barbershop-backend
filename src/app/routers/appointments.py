from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.app import crud
from src.app.database import get_db
from src.app.crud.appointment import create_appointment as create_appointment_crud, get_appointment_by_barber

from typing import List

from src.app.models.barber import Barber
from src.app.models.service import Service
from src.app.schemas.appointment import AppointmentCreate, AppointmentReadDetailed, AppointmentResponse


router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    created = create_appointment_crud(db=db, data=appointment)
    if not created:
        raise HTTPException(status_code=400, detail="Invalid service or addon ID")

    barber = db.query(Barber).filter(Barber.id == created.barber_id).first()
    service = db.query(Service).filter(Service.id == created.service_id).first()

    return AppointmentResponse(
        id=created.id,
        name=created.name,
        phone_number=created.phone_number,
        barber_id=created.barber_id,
        barber_name=barber.name,
        service_id=created.service_id,
        service_name=service.name,
        addons=created.addons,
        total_price=created.total_price,
        total_duration=created.total_duration,
    )


@router.get("/barber/{barber_id}", response_model=List[AppointmentReadDetailed])
def get_appointments_by_barber(barber_id: int, db: Session = Depends(get_db)):
    try:
        return get_appointment_by_barber(db, barber_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    success = crud.appointment.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
