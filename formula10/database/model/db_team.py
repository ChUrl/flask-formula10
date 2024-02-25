from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class DbTeam(db.Model):
    """
    A constructor/team (name only).
    """
    __tablename__ = "team"

    def __init__(self, *, name: str):
        self.name = name  # Primary key

    @classmethod
    def from_csv(cls, row: List[str]):
        db_team: DbTeam = cls(name=str(row[0]))
        return db_team

    name: Mapped[str] = mapped_column(String(32), primary_key=True)