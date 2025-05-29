from typing import Optional, List

from pydantic import BaseModel


class BarberBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class BarberCreate(BarberBase):
    pass


class BarberRead(BarberBase):
    id: int

    model_config = {
        "from_attributes": True
    }


class AssignServices(BaseModel):
    service_ids: List[int]


class BarberUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
