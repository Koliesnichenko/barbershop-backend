from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator
from src.app.validators.accounts import validate_password_strength, validate_email


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str

    model_config = {
        "from_attributes": True
    }

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        return validate_email(value)

    model_config = {
        "from_attributes": True
    }
