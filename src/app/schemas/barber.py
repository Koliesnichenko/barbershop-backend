from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class BarberBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class BarberCreate(BarberBase):
    pass


class BarberRead(BarberBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AssignServices(BaseModel):
    service_ids: List[int]


class AssignAddons(BaseModel):
    addon_ids: List[int]


class BarberUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BarberOut(BaseModel):
    id: int
    name: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
