from sqlalchemy import ForeignKey, Table, Column

from src.app.database import Base

barber_service = Table(
    "barber_service",
    Base.metadata,
    Column("barber_id", ForeignKey("barbers.id"), primary_key=True),
    Column("service_id", ForeignKey("services.id"), primary_key=True),
)