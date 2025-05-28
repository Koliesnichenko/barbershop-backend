from typing import List

from pydantic import BaseModel

from src.app.schemas.barber import BarberRead


class ServiceBase(BaseModel):
    name: str
    duration: int
    price: int


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int
    barbers: List[BarberRead] = []

    model_config = {
        "from_attributes": True
    }
