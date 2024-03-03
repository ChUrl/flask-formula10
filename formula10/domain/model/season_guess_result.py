from formula10.database.model.db_season_guess_result import DbSeasonGuessResult
from formula10.domain.model.user import User


class SeasonGuessResult():
    @classmethod
    def from_db_season_guess_result(cls, db_season_guess_result: DbSeasonGuessResult):
        season_guess_result: SeasonGuessResult = cls()
        season_guess_result.user = User.from_db_user(db_season_guess_result.user)
        season_guess_result.hot_take_correct = db_season_guess_result.hot_take_correct
        season_guess_result.overtakes_correct = db_season_guess_result.overtakes_correct

        return season_guess_result

    def to_db_season_guess_result(self) -> DbSeasonGuessResult:
        db_season_guess_result: DbSeasonGuessResult = DbSeasonGuessResult(user_id=self.user.id)
        db_season_guess_result.hot_take_correct = self.hot_take_correct
        db_season_guess_result.overtakes_correct = self.overtakes_correct
        return db_season_guess_result

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, SeasonGuessResult):
            return self.user == __value.user

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.user)

    user: User
    hot_take_correct: bool
    overtakes_correct: bool