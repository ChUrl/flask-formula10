from datetime import datetime
from typing import List
from urllib.parse import quote
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class Race(db.Model):
    """
    A single race at a certain date and GrandPrix in the calendar.
    It stores the place to guess for this race.
    """
    __tablename__ = "race"

    @staticmethod
    def from_csv(row: List[str]):
        race: Race = Race()
        race.name = str(row[0])
        race.number = int(row[1])
        race.date = datetime.strptime(row[2], "%Y-%m-%d")
        race.pxx = int(row[3])
        return race

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    number: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime)
    pxx: Mapped[int] = mapped_column(Integer)  # This is the place to guess