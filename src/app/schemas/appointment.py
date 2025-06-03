from pydantic import BaseModel, Field
from typing import List


class AppointmentCreate(BaseModel):
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    barber_id: int = Field(..., alias="barberId")
    service_id: int = Field(..., alias="serviceId")
    addon_ids: List[int] = Field(..., alias="addonIds")

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
    total_price: int

    model_config = {
        "from_attributes": True
    }


class AddonsOut(BaseModel):
    id: int
    name: str
    duration: int
    price: int

    model_config = {
        "from_attributes": True
    }


class AppointmentReadDetailed(BaseModel):
    id: int
    name: str
    phone_number: str
    barber_id: int
    service_id: int
    total_duration: int
    total_price: int
    addons: List[AddonsOut]

    model_config = {
        "from_attributes": True
    }


class AppointmentResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    barber_id: int
    barber_name: str
    service_id: int
    service_name: str
    addons: List[AddonsOut]
    total_duration: int
    total_price: int

    model_config = {
        "from_attributes": True
    }
