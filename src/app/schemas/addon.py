from typing import Optional, List

from pydantic import BaseModel

from src.app.schemas.barber import BarberRead


class AddonBase(BaseModel):
    name: str
    duration: int
    price: int


class AddonCreate(AddonBase):
    pass


class AddonRead(AddonBase):
    id: int
    barbers: List[BarberRead] = []

    model_config = {
        "from_attributes": True
    }


class AddonUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[int] = None
