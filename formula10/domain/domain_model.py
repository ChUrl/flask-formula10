from typing import Callable, List
from sqlalchemy import desc

from formula10.database.model.db_driver import DbDriver
from formula10.database.model.db_race import DbRace
from formula10.database.model.db_race_guess import DbRaceGuess
from formula10.database.model.db_race_result import DbRaceResult
from formula10.database.model.db_season_guess import DbSeasonGuess
from formula10.database.model.db_team import DbTeam
from formula10.database.model.db_user import DbUser
from formula10.database.validation import find_multiple_strict
from formula10.domain.model.driver import NONE_DRIVER, Driver
from formula10.domain.model.race import Race
from formula10.domain.model.race_guess import RaceGuess
from formula10.domain.model.race_result import RaceResult
from formula10.domain.model.season_guess import SeasonGuess
from formula10.domain.model.team import NONE_TEAM, Team
from formula10.domain.model.user import User
from formula10 import db


class Model():
    _all_users: List[User] | None = None
    _all_race_results: List[RaceResult] | None = None
    _all_race_guesses: List[RaceGuess] | None = None
    _all_season_guesses: List[SeasonGuess] | None = None
    _all_races: List[Race] | None = None
    _all_drivers: List[Driver] | None = None
    _all_teams: List[Team] | None = None

    def all_users(self) -> List[User]:
        """
        Returns a list of all users in the database.
        """
        if self._all_users is None:
            self._all_users = [
                User.from_db_user(db_user)
                for db_user in db.session.query(DbUser).filter_by(enabled=True).all()
            ]

        return self._all_users

    def all_race_results(self) -> List[RaceResult]:
        """
        Returns a list of all race results in the database, in descending order (most recent first).
        """
        if self._all_race_results is None:
            self._all_race_results = [
                RaceResult.from_db_race_result(db_race_result)
                for db_race_result in db.session.query(DbRaceResult).join(DbRaceResult.race).order_by(desc(DbRace.number)).all()
            ]

        return self._all_race_results

    def all_race_guesses(self) -> List[RaceGuess]:
        """
        Returns a list of all race guesses in the database.
        """
        if self._all_race_guesses is None:
            self._all_race_guesses = [
                RaceGuess.from_db_race_guess(db_race_guess)
                for db_race_guess in db.session.query(DbRaceGuess).join(DbRaceGuess.user).filter_by(enabled=True).all()  # Ignore disabled users
            ]

        return self._all_race_guesses

    def all_season_guesses(self) -> List[SeasonGuess]:
        if self._all_season_guesses is None:
            self._all_season_guesses = [
                SeasonGuess.from_db_season_guess(db_season_guess)
                for db_season_guess in db.session.query(DbSeasonGuess).join(DbSeasonGuess.user).filter_by(enabled=True).all()  # Ignore disabled users
            ]

        return self._all_season_guesses

    def all_races(self) -> List[Race]:
        """
        Returns a list of all races in the database.
        """
        if self._all_races is None:
            self._all_races = [
                Race.from_db_race(db_race)
                for db_race in db.session.query(DbRace).order_by(desc(DbRace.number)).all()
            ]

        return self._all_races

    def all_drivers(self, *, include_none: bool) -> List[Driver]:
        """
        Returns a list of all drivers in the database.
        """
        if self._all_drivers is None:
            self._all_drivers = [
                Driver.from_db_driver(db_driver)
                for db_driver in db.session.query(DbDriver).all()
            ]

        if include_none:
            return self._all_drivers
        else:
            predicate: Callable[[Driver], bool] = lambda driver: driver != NONE_DRIVER
            return find_multiple_strict(predicate, self._all_drivers)

    def all_teams(self, *, include_none: bool) -> List[Team]:
        """
        Returns a list of all teams in the database.
        """
        if self._all_teams is None:
            self._all_teams = [
                Team.from_db_team(db_team)
                for db_team in db.session.query(DbTeam).all()
            ]

        if include_none:
            return self._all_teams
        else:
            predicate: Callable[[Team], bool] = lambda team: team != NONE_TEAM
            return find_multiple_strict(predicate, self._all_teams)