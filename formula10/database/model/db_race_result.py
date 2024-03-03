from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.db_race import DbRace
from formula10 import db

class DbRaceResult(db.Model):
    """
    The result of a past race.
    It stores the corresponding race and dictionaries of place-/dnf-order and a list of drivers that are excluded from the standings for this race.
    """
    __tablename__ = "raceresult"

    def __init__(self, *, race_id: int):
        self.race_id = race_id  # Primary key

    race_id: Mapped[int] = mapped_column(ForeignKey("race.id"), primary_key=True)
    pxx_driver_ids_json: Mapped[str] = mapped_column(String(1024), nullable=False)
    first_dnf_driver_ids_json: Mapped[str] = mapped_column(String(1024), nullable=False)
    dnf_driver_ids_json: Mapped[str] = mapped_column(String(1024), nullable=False)
    excluded_driver_ids_json: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Relationships
    race: Mapped[DbRace] = relationship("DbRace", foreign_keys=[race_id])