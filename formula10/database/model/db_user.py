from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class DbUser(db.Model):
    """
    A user that can guess races (name only).
    """
    __tablename__ = "user"

    def __init__(self, *, id: int | None):
        if id is not None:
            self.id = id  # Primary key

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)