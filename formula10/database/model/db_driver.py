from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from formula10.database.model.db_team import DbTeam
from formula10 import db


class DbDriver(db.Model):
    """
    A F1 driver.
    It stores the corresponding team + name abbreviation.
    """
    __tablename__ = "driver"

    def __init__(self, *, id: int):
        self.id = id  # Primary key

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    abbr: Mapped[str] = mapped_column(String(4), nullable=False, unique=True)
    team_id: Mapped[str] = mapped_column(ForeignKey("team.id"), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)  # alpha-2 code
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    team: Mapped[DbTeam] = relationship("DbTeam", foreign_keys=[team_id])