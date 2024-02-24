from typing import Any, List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.user import User
from formula10.database.model.race import Race
from formula10.database.model.driver import Driver
from formula10 import db

class RaceGuess(db.Model):
    """
    A guess a user made for a race.
    It stores the corresponding race and the guessed drivers for PXX and DNF.
    """
    __tablename__ = "raceguess"
    __csv_header__ = ["user_name", "race_name", "pxx_driver_name", "dnf_driver_name"]

    def __init__(self, user_name: str, race_name: str):
        self.user_name = user_name  # Primary key
        self.race_name = race_name  # Primery key

    @staticmethod
    def from_csv(row: List[str]):
        race_guess: RaceGuess = RaceGuess(str(row[0]), str(row[1]))
        race_guess.pxx_driver_name = str(row[2])
        race_guess.dnf_driver_name = str(row[3])
        return race_guess

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.race_name,
            self.pxx_driver_name,
            self.dnf_driver_name
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_name])
    pxx: Mapped["Driver"] = relationship("Driver", foreign_keys=[pxx_driver_name])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_driver_name])