from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db

class Team(db.Model):
    """
    A constructor/team (name only).
    """
    __tablename__ = "team"

    @staticmethod
    def from_csv(row: List[str]):
        team: Team = Team()
        team.name = str(row[0])
        return team

    name: Mapped[str] = mapped_column(String(32), primary_key=True)