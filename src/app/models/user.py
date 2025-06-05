from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from src.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(default="user")

    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="user")
