from sqlalchemy import Table, ForeignKey, Column

from src.app.database import Base

barber_addon = Table(
    "barber_addon",
    Base.metadata,
    Column("barber_id", ForeignKey("barbers.id"), primary_key=True),
    Column("addon_id", ForeignKey("addons.id"), primary_key=True),
)
