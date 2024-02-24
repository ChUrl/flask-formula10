import json
from typing import Any, Dict, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.driver import Driver
from formula10.database.model.race import Race
from formula10 import db

class RaceResult(db.Model):
    """
    The result of a past race.
    It stores the corresponding race and dictionaries of place-/dnf-order and a list of drivers that are excluded from the standings for this race.
    """
    __tablename__ = "raceresult"
    __allow_unmapped__ = True  # TODO: Used for json conversion, move this to some other class instead
    __csv_header__ = ["race_name", "pxx_driver_names_json", "first_dnf_driver_names_json", "dnf_driver_names_json", "excluded_driver_names_json"]

    def __init__(self, race_name: str):
        self.race_name = race_name  # Primary key

    @staticmethod
    def from_csv(row: List[str]):
        race_result: RaceResult = RaceResult(str(row[0]))
        race_result.pxx_driver_names_json = str(row[1])
        race_result.first_dnf_driver_names_json = str(row[2])
        race_result.dnf_driver_names_json = str(row[3])
        race_result.excluded_driver_names_json = str(row[4])
        return race_result

    def to_csv(self) -> List[Any]:
        return [
            self.race_name,
            self.pxx_driver_names_json,
            self.first_dnf_driver_names_json,
            self.dnf_driver_names_json,
            self.excluded_driver_names_json
        ]

    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)
    first_dnf_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)
    dnf_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)
    excluded_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)

    @property
    def pxx_driver_names(self) -> Dict[str, str]:
        return json.loads(self.pxx_driver_names_json)

    @pxx_driver_names.setter
    def pxx_driver_names(self, new_pxx_driver_names: Dict[str, str]):
        self.pxx_driver_names_json = json.dumps(new_pxx_driver_names)

    @property
    def first_dnf_driver_names(self) -> List[str]:
        return json.loads(self.first_dnf_driver_names_json)

    @first_dnf_driver_names.setter
    def first_dnf_driver_names(self, new_first_dnf_driver_names: List[str]):
        self.first_dnf_driver_names_json = json.dumps(new_first_dnf_driver_names)

    @property
    def dnf_driver_names(self) -> List[str]:
        return json.loads(self.dnf_driver_names_json)

    @dnf_driver_names.setter
    def dnf_driver_names(self, new_dnf_driver_names: List[str]):
        self.dnf_driver_names_json = json.dumps(new_dnf_driver_names)

    @property
    def excluded_driver_names(self) -> List[str]:
        return json.loads(self.excluded_driver_names_json)

    @excluded_driver_names.setter
    def excluded_driver_names(self, new_excluded_driver_names: List[str]):
        self.excluded_driver_names_json = json.dumps(new_excluded_driver_names)

    # Relationships
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_name])
    _pxx_drivers: Dict[str, Driver] | None = None
    _first_dnf_drivers: List[Driver] | None = None
    _dnf_drivers: List[Driver] | None = None
    _excluded_drivers: List[Driver] | None = None

    @property
    def pxx_drivers(self) -> Dict[str, Driver]:
        if self._pxx_drivers is None:
            self._pxx_drivers = dict()
            for position, driver_name in self.pxx_driver_names.items():
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._pxx_drivers[position] = driver

        return self._pxx_drivers

    def pxx_driver(self, offset: int = 0) -> Driver | None:
        pxx_num: str = str(self.race.pxx + offset)

        if pxx_num not in self.pxx_drivers:
            raise Exception(f"Position {pxx_num} not found in RaceResult.pxx_drivers")

        if self.pxx_drivers[pxx_num].name in self.excluded_driver_names:
            none_driver: Driver | None = db.session.query(Driver).filter_by(name="None").first()
            if none_driver is None:
                raise Exception(f"NONE-driver not found in database")

            return none_driver


        return self.pxx_drivers[pxx_num]

    def pxx_driver_position_string(self, driver_name: str) -> str:
        for position, driver in self.pxx_driver_names.items():
            if driver == driver_name and driver not in self.excluded_driver_names:
                return f"P{position}"

        return "NC"

    @property
    def all_positions(self) -> List[Driver]:
        return [
            self.pxx_drivers[str(position)] for position in range(1, 21)
        ]

    @property
    def first_dnf_drivers(self) -> List[Driver]:
        if self._first_dnf_drivers is None:
            self._first_dnf_drivers = list()
            for driver_name in self.first_dnf_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._first_dnf_drivers.append(driver)

            if len(self._first_dnf_drivers) == 0:
                none_driver: Driver | None = db.session.query(Driver).filter_by(name="None").first()
                if none_driver is None:
                    raise Exception("NONE-driver not found in database")

                self._first_dnf_drivers.append(none_driver)

        return self._first_dnf_drivers

    @property
    def dnf_drivers(self) -> List[Driver]:
        if self._dnf_drivers is None:
            self._dnf_drivers = list()
            for driver_name in self.dnf_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._dnf_drivers.append(driver)

        return self._dnf_drivers

    @property
    def excluded_drivers(self) -> List[Driver]:
        if self._excluded_drivers is None:
            self._excluded_drivers = list()
            for driver_name in self.excluded_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._excluded_drivers.append(driver)

        return self._excluded_drivers