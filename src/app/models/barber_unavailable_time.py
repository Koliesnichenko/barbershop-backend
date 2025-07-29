from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class BarberUnavailableTime(Base):
    __tablename__ = "barber_unavailable_times"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    barber_id: Mapped[int] = mapped_column(Integer, ForeignKey("barbers.id"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=True)

    barber: Mapped["Barber"] = relationship("Barber", back_populates="unavailable_times")

    def __repr__(self):
        return (f"<BarberUnavailableTime(barber_id={self.barber_id},"
                f" start={self.start_time},"
                f" end={self.end_time}, reason={self.reason})>")
