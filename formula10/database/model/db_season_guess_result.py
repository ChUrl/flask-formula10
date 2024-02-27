from typing import List

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10 import db
from formula10.database.model.db_user import DbUser

class DbSeasonGuessResult(db.Model):
    """
    Manually entered results for the season bonus guesses.
    """

    __tablename__ = "seasonguessresult"
    __csv_header__ = ["user_name", "hot_take_correct", "overtakes_correct"]

    def __init__(self, *, user_name: str, hot_take_correct: bool, overtakes_correct: bool):
        self.user_name = user_name  # Primary key

        self.hot_take_correct = hot_take_correct
        self.overtakes_correct = overtakes_correct

    @classmethod
    def from_csv(cls, row: List[str]):
        db_season_guess_result: DbSeasonGuessResult = cls(user_name=str(row[0]),
                                                          hot_take_correct=True if str(row[1])=="True" else False,
                                                          overtakes_correct=True if str(row[2])=="True" else False)

        return db_season_guess_result

    # This object can't be edited from the page context
    # def to_csv(self) -> List[Any]:
    #     return [
    #         self.user_name,
    #         self.hot_take_correct,
    #         self.overtakes_correct
    #     ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    hot_take_correct: Mapped[bool] = mapped_column(Boolean)
    overtakes_correct: Mapped[bool] = mapped_column(Boolean)

    # Relationships
    user: Mapped[DbUser] = relationship("DbUser", foreign_keys=[user_name])
