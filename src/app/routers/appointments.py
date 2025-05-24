from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.app.schemas import AppointmentCreate, AppointmentRead
from src.app.database import get_db
from src.app import crud

router = APIRouter()


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        new_appointment = crud.create_appointment(db=db, data=appointment)
        return {"id": new_appointment.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))