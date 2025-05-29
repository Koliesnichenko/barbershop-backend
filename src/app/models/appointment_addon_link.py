from sqlalchemy import ForeignKey, Table, Column

from src.app.database import Base

appointment_addon = Table(
    "appointment_addon",
    Base.metadata,
    Column("appointment_id", ForeignKey("appointments.id"), primary_key=True),
    Column("addon_id", ForeignKey("addons.id"), primary_key=True),
)