from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    duration: int
    price: int


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int

    model_config = {
        "from_attributes": True
    }
