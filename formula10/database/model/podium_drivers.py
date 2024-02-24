import json
from typing import Any, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.user import User
from formula10.database.model.driver import Driver
from formula10 import db


class PodiumDrivers(db.Model):
    """
    A guessed list of each driver that will reach at least a single podium.
    """
    __tablename__ = "podiumdrivers"
    __allow_unmapped__ = True
    __csv_header__ = ["user_name", "podium_driver_names_json"]

    def __init__(self, user_name: str):
        self.user_name = user_name

    @staticmethod
    def from_csv(row: List[str]):
        podium_drivers: PodiumDrivers = PodiumDrivers(str(row[0]))
        podium_drivers.podium_driver_names_json = str(row[1])
        return podium_drivers

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.podium_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    podium_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)

    @property
    def podium_driver_names(self) -> List[str]:
        return json.loads(self.podium_driver_names_json)

    @podium_driver_names.setter
    def podium_driver_names(self, new_podium_driver_names: List[str]):
        self.podium_driver_names_json = json.dumps(new_podium_driver_names)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    _podium_drivers: List[Driver] | None = None

    @property
    def podium_drivers(self) -> List[Driver]:
        if self._podium_drivers is None:
            self._podium_drivers = list()
            for driver_name in self.podium_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._podium_drivers.append(driver)

        return self._podium_drivers