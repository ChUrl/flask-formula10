from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from formula10.database.model.db_team import DbTeam
from formula10 import db


class DbDriver(db.Model):
    """
    A F1 driver.
    It stores the corresponding team + name abbreviation.
    """
    __tablename__ = "driver"

    def __init__(self, *, name: str):
        self.name = name  # Primary key

    @classmethod
    def from_csv(cls, row: List[str]):
        db_driver: DbDriver = cls(name=str(row[0]))
        db_driver.abbr = str(row[1])
        db_driver.team_name = str(row[2])
        db_driver.country_code = str(row[3])
        return db_driver

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    abbr: Mapped[str] = mapped_column(String(4))
    team_name: Mapped[str] = mapped_column(ForeignKey("team.name"))
    country_code: Mapped[str] = mapped_column(String(2))  # alpha-2 code

    # Relationships
    team: Mapped[DbTeam] = relationship("DbTeam", foreign_keys=[team_name])