from typing import Any, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.driver import Driver
from formula10.database.model.podium_drivers import PodiumDrivers
from formula10.database.model.team import Team
from formula10.database.model.team_winners import TeamWinners
from formula10.database.model.user import User
from formula10 import db

class SeasonGuess(db.Model):
    """
    A collection of bonus guesses for the entire season.
    """
    __tablename__ = "seasonguess"
    __csv_header__ = ["user_name", "hot_take", "p2_team_name",
                      "overtake_driver_name", "dnf_driver_name", "gained_driver_name", "lost_driver_name",
                      "team_winners_id", "podium_drivers_id"]

    def __init__(self, user_name: str, team_winners_user_name: str | None = None, podium_drivers_user_name: str | None = None):
        self.user_name = user_name  # Primary key

        # Although this is the same username, handle separately, in case they don't exist in the database yet
        if team_winners_user_name is not None:
            if user_name != team_winners_user_name:
                raise Exception(f"SeasonGuess for {user_name} was supplied TeamWinners for {team_winners_user_name}")

            self.team_winners_id = team_winners_user_name

        if podium_drivers_user_name is not None:
            if user_name != podium_drivers_user_name:
                raise Exception(f"SeasonGuess for {user_name} was supplied PodiumDrivers for {podium_drivers_user_name}")

            self.podium_drivers_id = podium_drivers_user_name

    @staticmethod
    def from_csv(row: List[str]):
        season_guess: SeasonGuess = SeasonGuess(str(row[0]), team_winners_user_name=str(row[7]), podium_drivers_user_name=str(row[8]))
        season_guess.hot_take = str(row[1])
        season_guess.p2_team_name = str(row[2])
        season_guess.overtake_driver_name = str(row[3])
        season_guess.dnf_driver_name = str(row[4])
        season_guess.gained_driver_name = str(row[5])
        season_guess.lost_driver_name = str(row[6])
        return season_guess

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.hot_take,
            self.p2_team_name,
            self.overtake_driver_name,
            self.dnf_driver_name,
            self.gained_driver_name,
            self.lost_driver_name,
            self.team_winners_id,
            self.podium_drivers_id
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    hot_take: Mapped[str] = mapped_column(String(512), nullable=True)
    p2_team_name: Mapped[str] = mapped_column(ForeignKey("team.name"), nullable=True)
    overtake_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    gained_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    lost_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)

    team_winners_id: Mapped[str] = mapped_column(ForeignKey("teamwinners.user_name"))
    podium_drivers_id: Mapped[str] = mapped_column(ForeignKey("podiumdrivers.user_name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    p2_team: Mapped["Team"] = relationship("Team", foreign_keys=[p2_team_name])
    overtake_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[overtake_driver_name])
    dnf_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_driver_name])
    gained_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[gained_driver_name])
    lost_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[lost_driver_name])

    team_winners: Mapped["TeamWinners"] = relationship("TeamWinners", foreign_keys=[team_winners_id])
    podium_drivers: Mapped["PodiumDrivers"] = relationship("PodiumDrivers", foreign_keys=[podium_drivers_id])