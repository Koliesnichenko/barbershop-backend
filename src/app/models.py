from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.app.database import Base

appointments_addons = Table(
    "appointments_addons",
    Base.metadata,
    Column("appointment_id", ForeignKey("appointments.id"), primary_key=True),
    Column("addon_id", ForeignKey("addons.id"), primary_key=True),
)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()
    barber_id: Mapped[int] = mapped_column()
    service_id: Mapped[int] = mapped_column()
    total_duration: Mapped[int] = mapped_column()
    total_price: Mapped[int] = mapped_column()

    addons = relationship("Addon", secondary=appointments_addons, back_populates="appointments")


class Addon(Base):
    __tablename__ = "addons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column()
    price: Mapped[int] = mapped_column()
    category: Mapped[str] = mapped_column()

    appointments = relationship("Appointment", secondary=appointments_addons, back_populates="addons")
