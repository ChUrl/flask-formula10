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

    def __init__(self, *, user_id: int, race_id: int):
        self.user_id = user_id  # Primary key
        self.race_id = race_id  # Primary key

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("race.id"), primary_key=True)
    pxx_driver_id: Mapped[int] = mapped_column(ForeignKey("driver.id"), nullable=False)
    dnf_driver_id: Mapped[int] = mapped_column(ForeignKey("driver.id"), nullable=False)

    # Relationships
    user: Mapped[DbUser] = relationship("DbUser", foreign_keys=[user_id])
    race: Mapped[DbRace] = relationship("DbRace", foreign_keys=[race_id])
    pxx: Mapped[DbDriver] = relationship("DbDriver", foreign_keys=[pxx_driver_id])
    dnf: Mapped[DbDriver] = relationship("DbDriver", foreign_keys=[dnf_driver_id])