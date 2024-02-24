import json
from typing import Any, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.driver import Driver
from formula10.database.model.user import User
from formula10 import db

class TeamWinners(db.Model):
    """
    A guessed list of each best driver per team.
    """
    __tablename__ = "teamwinners"
    __allow_unmapped__ = True
    __csv_header__ = ["user_name", "teamwinner_driver_names_json"]

    def __init__(self, user_name: str):
        self.user_name = user_name  # Primary key

    @staticmethod
    def from_csv(row: List[str]):
        team_winners: TeamWinners = TeamWinners(str(row[0]))
        team_winners.teamwinner_driver_names_json = str(row[1])
        return team_winners

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.teamwinner_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    teamwinner_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)

    @property
    def teamwinner_driver_names(self) -> List[str]:
        return json.loads(self.teamwinner_driver_names_json)

    @teamwinner_driver_names.setter
    def teamwinner_driver_names(self, new_teamwinner_driver_names: List[str]):
        self.teamwinner_driver_names_json = json.dumps(new_teamwinner_driver_names)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    _teamwinner_drivers: List[Driver] | None = None

    @property
    def teamwinners(self) -> List[Driver]:
        if self._teamwinner_drivers is None:
            self._teamwinner_drivers = list()
            for driver_name in self.teamwinner_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._teamwinner_drivers.append(driver)

        return self._teamwinner_drivers