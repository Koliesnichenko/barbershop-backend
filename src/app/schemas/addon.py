from typing import Optional

from pydantic import BaseModel


class AddonBase(BaseModel):
    name: str
    duration: int
    price: int
    category: str


class AddonCreate(AddonBase):
    pass


class AddonRead(AddonBase):
    id: int

    model_config = {
        "from_attributes": True
    }


class AddonUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[int] = None
    category: Optional[str] = None
