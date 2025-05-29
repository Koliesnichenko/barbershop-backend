from typing import List, Optional

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


class ServiceUpdate(ServiceBase):
    name: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[int] = None
    category: Optional[str] = None
