from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class DbRace(db.Model):
    """
    A single race at a certain date and GrandPrix in the calendar.
    It stores the place to guess for this race.
    """
    __tablename__ = "race"

    def __init__(self, *, id: int):
        self.id = id  # Primary key

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, unique=True)
    pxx: Mapped[int] = mapped_column(Integer, nullable=False)  # This is the place to guess