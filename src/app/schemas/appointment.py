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

    model_config = {
        "validate_by_name": True
    }


class AppointmentRead(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }


class AppointmentList(BaseModel):
    id: int
    name: str
    phone_number: str
    barber_id: int
    service_id: int
    total_duration: int
    total_price: str

    model_config = {
        "from_attributes": True
    }
