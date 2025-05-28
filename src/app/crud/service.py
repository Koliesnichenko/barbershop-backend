from sqlalchemy.orm import Session

from src.app.models.service import Service
from src.app.schemas.service import ServiceCreate


def create_service(db: Session, service: ServiceCreate):
    new_service = Service(**service.model_dump())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


def get_services(db: Session):
    return db.query(Service).all()


def get_service(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()


def delete_service(db: Session, service_id: int):
    service = get_service(db, service_id)
    if service:
        db.delete(service)
        db.commit()
        return True
    return False
