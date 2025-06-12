from datetime import time

from sqlalchemy import Integer, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.database import Base


class BarberSchedule(Base):
    __tablename__ = "barber_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    barber_id: Mapped[int] = mapped_column(Integer, ForeignKey("barbers.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    barber: Mapped["Barber"] = relationship("Barber", back_populates="schedules")

    def __repr__(self):
        return (f"<BarberSchedule(barber_id={self.barber_id},"
                f" day_of_week={self.day_of_week},"
                f" start={self.start_time}, end={self.end_time})>")
