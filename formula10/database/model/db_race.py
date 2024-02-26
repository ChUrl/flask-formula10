from datetime import datetime
from typing import List
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class DbRace(db.Model):
    """
    A single race at a certain date and GrandPrix in the calendar.
    It stores the place to guess for this race.
    """
    __tablename__ = "race"

    def __init__(self, *, name: str, number: int, date: datetime, pxx: int):
        self.name = name  # Primary key

        self.number = number
        self.date = date
        self.pxx = pxx

    @classmethod
    def from_csv(cls, row: List[str]):
        db_race: DbRace = cls(name=str(row[0]),
                              number=int(row[1]),
                              date=datetime.strptime(str(row[2]), "%Y-%m-%d-%H-%M"),
                              pxx=int(row[3]))
        return db_race

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    number: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime)
    pxx: Mapped[int] = mapped_column(Integer)  # This is the place to guess