from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app.crud import service as crud
from src.app.schemas.service import ServiceCreate, ServiceRead, ServiceBase
from typing import List

router = APIRouter(tags=["Services"])


@router.post("/", response_model=ServiceRead)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return crud.create_service(db=db, service=service)


@router.get("/", response_model=List[ServiceRead])
def get_all_services(db: Session = Depends(get_db)):
    return crud.get_services(db=db)


@router.put("/{service_id}", response_model=ServiceRead)
def update_service(service_id: int, updated_data: ServiceBase, db: Session = Depends(get_db)):
    result = crud.update_service(db=db, service_id=service_id, updated_data=updated_data)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    if not crud.delete_service(db=db, service_id=service_id):
        raise HTTPException(status_code=404, detail="Service not found")
