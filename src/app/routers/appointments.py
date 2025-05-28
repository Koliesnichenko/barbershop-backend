from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app import crud
from typing import List
from src.app.schemas.appointment import AppointmentCreate, AppointmentRead, AppointmentList, AppointmentReadDetailed

router = APIRouter()


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        new_appointment = crud.create_appointment(db=db, data=appointment)
        return {"id": new_appointment.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/barber/{barber_id}", response_model=List[AppointmentReadDetailed])
def get_appointments_by_barber(barber_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_appointment_by_barber(db, barber_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    success = crud.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
