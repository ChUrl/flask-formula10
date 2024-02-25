from typing import Any, List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.db_user import DbUser
from formula10.database.model.db_race import DbRace
from formula10.database.model.db_driver import DbDriver
from formula10 import db


class DbRaceGuess(db.Model):
    """
    A guess a user made for a race.
    It stores the corresponding race and the guessed drivers for PXX and DNF.
    """
    __tablename__ = "raceguess"
    __csv_header__ = ["user_name", "race_name", "pxx_driver_name", "dnf_driver_name"]

    def __init__(self, *, user_name: str, race_name: str, pxx_driver_name: str, dnf_driver_name: str):
        self.user_name = user_name  # Primary key
        self.race_name = race_name  # Primary key

        self.dnf_driver_name = dnf_driver_name
        self.pxx_driver_name = pxx_driver_name

    @classmethod
    def from_csv(cls, row: List[str]):
        db_race_guess: DbRaceGuess = cls(user_name=str(row[0]),
                                         race_name=str(row[1]),
                                         pxx_driver_name=str(row[2]),
                                         dnf_driver_name=str(row[3]))
        return db_race_guess

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.race_name,
            self.pxx_driver_name,
            self.dnf_driver_name
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    user: Mapped[DbUser] = relationship("DbUser", foreign_keys=[user_name])
    race: Mapped[DbRace] = relationship("DbRace", foreign_keys=[race_name])
    pxx: Mapped[DbDriver] = relationship("DbDriver", foreign_keys=[pxx_driver_name])
    dnf: Mapped[DbDriver] = relationship("DbDriver", foreign_keys=[dnf_driver_name])