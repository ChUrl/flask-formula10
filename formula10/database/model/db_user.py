from typing import Any, List
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db


class DbUser(db.Model):
    """
    A user that can guess races (name only).
    """
    __tablename__ = "user"
    __csv_header__ = ["name", "enabled"]

    def __init__(self, *, name: str, enabled: bool):
        self.name = name  # Primary key

        self.enabled = enabled

    @classmethod
    def from_csv(cls, row: List[str]):
        db_user: DbUser = cls(name=str(row[0]), enabled=True if str(row[1])=="True" else False)
        return db_user

    def to_csv(self) -> List[Any]:
        return [
            self.name,
            self.enabled
        ]

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean)