from typing import Optional

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
