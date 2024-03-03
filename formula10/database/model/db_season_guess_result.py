from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from formula10 import db
from formula10.database.model.db_user import DbUser

class DbSeasonGuessResult(db.Model):
    """
    Manually entered results for the season bonus guesses.
    """

    __tablename__ = "seasonguessresult"

    def __init__(self, *, user_id: int):
        self.user_id = user_id  # Primary key

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    hot_take_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    overtakes_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    user: Mapped[DbUser] = relationship("DbUser", foreign_keys=[user_id])
