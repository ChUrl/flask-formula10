from typing import Any, List
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
    __csv_header__ = ["race_name", "pxx_driver_names_json", "first_dnf_driver_names_json", "dnf_driver_names_json", "excluded_driver_names_json"]

    def __init__(self, *, race_name: str, pxx_driver_names_json: str, first_dnf_driver_names_json: str, dnf_driver_names_json: str, excluded_driver_names_json: str):
        self.race_name = race_name  # Primary key

        self.pxx_driver_names_json = pxx_driver_names_json
        self.first_dnf_driver_names_json = first_dnf_driver_names_json
        self.dnf_driver_names_json = dnf_driver_names_json
        self.excluded_driver_names_json = excluded_driver_names_json

    @classmethod
    def from_csv(cls, row: List[str]):
        db_race_result: DbRaceResult = cls(race_name=str(row[0]),
                                           pxx_driver_names_json=str(row[1]),
                                           first_dnf_driver_names_json=str(row[2]),
                                           dnf_driver_names_json=str(row[3]),
                                           excluded_driver_names_json=str(row[4]))
        return db_race_result

    def to_csv(self) -> List[Any]:
        return [
            self.race_name,
            self.pxx_driver_names_json,
            self.first_dnf_driver_names_json,
            self.dnf_driver_names_json,
            self.excluded_driver_names_json
        ]

    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_names_json: Mapped[str] = mapped_column(String(1024))
    first_dnf_driver_names_json: Mapped[str] = mapped_column(String(1024))
    dnf_driver_names_json: Mapped[str] = mapped_column(String(1024))
    excluded_driver_names_json: Mapped[str] = mapped_column(String(1024))

    # Relationships
    race: Mapped[DbRace] = relationship("DbRace", foreign_keys=[race_name])