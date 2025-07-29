from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.models.barber_addon_link import barber_addon
from src.app.models.barber_schedule import BarberSchedule
from src.app.models.barber_service_link import barber_service

from src.app.database import Base
from src.app.models.barber_unavailable_time import BarberUnavailableTime


class Barber(Base):
    __tablename__ = "barbers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    avatar_url: Mapped[str] = mapped_column(nullable=True)

    services = relationship("Service", secondary=barber_service, back_populates="barbers")

    addons = relationship("Addon", secondary=barber_addon, back_populates="barbers")

    schedules: Mapped[list["BarberSchedule"]] = relationship(
        "BarberSchedule", back_populates="barber", cascade="all, delete-orphan"
    )
    unavailable_times: Mapped[list["BarberUnavailableTime"]] = relationship(
        "BarberUnavailableTime", back_populates="barber", cascade="all, delete-orphan"
    )
