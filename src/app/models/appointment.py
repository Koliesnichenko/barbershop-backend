from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.app.database import Base
from src.app.models.appointment_addon_link import appointment_addon


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()
    barber_id: Mapped[int] = mapped_column()
    service_id: Mapped[int] = mapped_column()
    total_duration: Mapped[int] = mapped_column()
    total_price: Mapped[int] = mapped_column()

    addons = relationship("Addon", secondary=appointment_addon, back_populates="appointments")
