from pydantic import BaseModel
from typing import List


class AppointmentCreate(BaseModel):
    name: str
    phoneNumber: str
    barberId: int
    serviceId: int
    addonIds: List[int]
    totalDuration: int
    totalPrice: str


class AppointmentRead(BaseModel):
    id: int

    class Config:
        orm_mode = True
