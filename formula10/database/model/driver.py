from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from formula10.database.model.team import Team
from formula10 import db


class Driver(db.Model):
    """
    A F1 driver.
    It stores the corresponding team + name abbreviation.
    """
    __tablename__ = "driver"

    @staticmethod
    def from_csv(row: List[str]):
        driver: Driver = Driver()
        driver.name = str(row[0])
        driver.abbr = str(row[1])
        driver.team_name = str(row[2])
        driver.country_code = str(row[3])
        return driver

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    abbr: Mapped[str] = mapped_column(String(4))
    team_name: Mapped[str] = mapped_column(ForeignKey("team.name"))
    country_code: Mapped[str] = mapped_column(String(2))  # alpha-2 code

    # Relationships
    team: Mapped["Team"] = relationship("Team", foreign_keys=[team_name])