from pydantic import BaseModel, Field
from typing import List


class AppointmentCreate(BaseModel):
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    barber_id: int = Field(..., alias="barberId")
    service_id: int = Field(..., alias="serviceId")
    addon_ids: List[int] = Field(..., alias="addonIds")
    total_duration: int = Field(..., alias="totalDuration")
    total_price: str = Field(..., alias="totalPrice")

    class Config:
        allow_population_by_field_name = True


class AppointmentRead(BaseModel):
    id: int

    class Config:
        orm_mode = True
