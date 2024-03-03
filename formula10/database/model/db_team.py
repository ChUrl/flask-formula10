from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class DbTeam(db.Model):
    """
    A constructor/team (name only).
    """
    __tablename__ = "team"

    def __init__(self, *, id: int):
        self.id = id  # Primary key

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)