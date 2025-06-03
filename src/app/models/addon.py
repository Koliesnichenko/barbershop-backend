from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.app.database import Base
from src.app.models.appointment_addon_link import appointment_addon
from src.app.models.barber_addon_link import barber_addon
from src.app.models import appointment


class Addon(Base):
    __tablename__ = "addons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column()
    price: Mapped[int] = mapped_column()

    appointments = relationship("Appointment", secondary=appointment_addon, back_populates="addons")
    barbers = relationship("Barber", secondary=barber_addon, back_populates="addons")
