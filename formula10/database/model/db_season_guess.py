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

    def __init__(self, *, user_id: int):
        self.user_id = user_id  # Primary key

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    hot_take: Mapped[str | None] = mapped_column(String(512), nullable=True)
    p2_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), nullable=True)
    overtake_driver_id: Mapped[int | None] = mapped_column(ForeignKey("driver.id"), nullable=True)
    dnf_driver_id: Mapped[int | None] = mapped_column(ForeignKey("driver.id"), nullable=True)
    gained_driver_id: Mapped[int | None] = mapped_column(ForeignKey("driver.id"), nullable=True)
    lost_driver_id: Mapped[int | None] = mapped_column(ForeignKey("driver.id"), nullable=True)
    team_winners_driver_ids_json: Mapped[str] = mapped_column(String(1024))
    podium_drivers_driver_ids_json: Mapped[str] = mapped_column(String(1024))

    # Relationships
    user: Mapped[DbUser] = relationship("DbUser", foreign_keys=[user_id])
    p2_team: Mapped[DbTeam | None] = relationship("DbTeam", foreign_keys=[p2_team_id])
    overtake_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[overtake_driver_id])
    dnf_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[dnf_driver_id])
    gained_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[gained_driver_id])
    lost_driver: Mapped[DbDriver | None] = relationship("DbDriver", foreign_keys=[lost_driver_id])