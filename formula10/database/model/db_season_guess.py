from typing import Any, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10.database.model.db_driver import DbDriver
from formula10.database.model.db_team import DbTeam
from formula10.database.model.db_user import DbUser
from formula10 import db

class DbSeasonGuess(db.Model):
    """
    A collection of bonus guesses for the entire season.
    """
    __tablename__ = "seasonguess"
    __csv_header__ = ["user_name", "hot_take", "p2_team_name",
                      "overtake_driver_name", "dnf_driver_name", "gained_driver_name", "lost_driver_name",
                      "team_winners_driver_names_json", "podium_drivers_driver_names_json"]

    def __init__(self, *, user_name: str, team_winners_driver_names_json: str, podium_drivers_driver_names_json: str):
        self.user_name = user_name  # Primary key

        self.team_winners_driver_names_json = team_winners_driver_names_json
        self.podium_drivers_driver_names_json = podium_drivers_driver_names_json

    @classmethod
    def from_csv(cls, row: List[str]):
        db_season_guess: DbSeasonGuess = cls(user_name=str(row[0]),
                                             team_winners_driver_names_json=str(row[7]),
                                             podium_drivers_driver_names_json=str(row[8]))
        db_season_guess.hot_take = str(row[1])
        db_season_guess.p2_team_name = str(row[2])
        db_season_guess.overtake_driver_name = str(row[3])
        db_season_guess.dnf_driver_name = str(row[4])
        db_season_guess.gained_driver_name = str(row[5])
        db_season_guess.lost_driver_name = str(row[6])
        return db_season_guess

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.hot_take,
            self.p2_team_name,
            self.overtake_driver_name,
            self.dnf_driver_name,
            self.gained_driver_name,
            self.lost_driver_name,
            self.team_winners_driver_names_json,
            self.podium_drivers_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    hot_take: Mapped[str | None] = mapped_column(String(512), nullable=True)
    p2_team_name: Mapped[str | None] = mapped_column(ForeignKey("team.name"), nullable=True)
    overtake_driver_name: Mapped[str | None] = mapped_column(ForeignKey("driver.name"), nullable=True)
    dnf_driver_name: Mapped[str | None] = mapped_column(ForeignKey("driver.name"), nullable=True)
    gained_driver_name: Mapped[str | None] = mapped_column(ForeignKey("driver.name"), nullable=True)
    lost_driver_name: Mapped[str | None] = mapped_column(ForeignKey("driver.name"), nullable=True)
    team_winners_driver_names_json: Mapped[str] = mapped_column(String(1024))
    podium_drivers_driver_names_json: Mapped[str] = mapped_column(String(1024))

    # Relationships
    user: Mapped[DbUser] = relationship("DbUser", foreign_keys=[user_name])
    p2_team: Mapped[DbTeam | None] = relationship("DbTeam", foreign_keys=[p2_team_name])
    overtake_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[overtake_driver_name])
    dnf_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[dnf_driver_name])
    gained_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[gained_driver_name])
    lost_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[lost_driver_name])