from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.app.models.barber_service_link import barber_service

from src.app.database import Base


class Barber(Base):
    __tablename__ = "barbers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    avatar_url: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(default="barber")

    services = relationship("Service", secondary="barber_service", back_populates="barbers")
