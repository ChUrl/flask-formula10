from typing import Any, List
from urllib.parse import quote
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from formula10 import db

class User(db.Model):
    """
    A user that can guess races (name only).
    """
    __tablename__ = "user"
    __csv_header__ = ["name"]

    def __init__(self, name: str):
        self.name = name  # Primary key

    @staticmethod
    def from_csv(row: List[str]):
        user: User = User(str(row[0]))
        return user

    def to_csv(self) -> List[Any]:
        return [
            self.name
        ]

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)

    name: Mapped[str] = mapped_column(String(32), primary_key=True)