from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app.crud import barber as crud
from src.app.schemas.barber import BarberCreate, BarberRead, BarberBase
from typing import List

router = APIRouter(tags=["Barbers"])


@router.post("/", response_model=BarberRead)
def create_barber(barber: BarberCreate, db: Session = Depends(get_db)):
    return crud.create_barber(db=db, barber=barber)


@router.get("/", response_model=List[BarberRead])
def get_all_barbers(db: Session = Depends(get_db)):
    return crud.get_barbers(db=db)


@router.put("/{barber_id}", response_model=BarberRead)
def update_barber(barber_id: int, updated_data: BarberBase, db: Session = Depends(get_db)):
    result = crud.update_barber(db=db, barber_id=barber_id, updated_data=updated_data)
    if not result:
        raise HTTPException(status_code=404, detail="Barber not found")
    return result


@router.delete("/{barber_id}", status_code=204)
def delete_barber(barber_id: int, db: Session = Depends(get_db)):
    if not crud.delete_barber(db=db, barber_id=barber_id):
        raise HTTPException(status_code=404, detail="Barber not found")
