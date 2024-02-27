from typing import Callable, Dict, List, overload
from sqlalchemy import desc

from formula10.database.model.db_driver import DbDriver
from formula10.database.model.db_race import DbRace
from formula10.database.model.db_race_guess import DbRaceGuess
from formula10.database.model.db_race_result import DbRaceResult
from formula10.database.model.db_season_guess import DbSeasonGuess
from formula10.database.model.db_team import DbTeam
from formula10.database.model.db_user import DbUser
from formula10.database.validation import find_multiple_strict, find_single_or_none_strict, find_single_strict
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
        Returns a list of all enabled users.
        """
        if self._all_users is None:
            self._all_users = [
                User.from_db_user(db_user)
                for db_user in db.session.query(DbUser).filter_by(enabled=True).all()
            ]

        return self._all_users

    def all_race_results(self) -> List[RaceResult]:
        """
        Returns a list of all race results, in descending order (most recent first).
        """
        if self._all_race_results is None:
            self._all_race_results = [
                RaceResult.from_db_race_result(db_race_result)
                for db_race_result in db.session.query(DbRaceResult).join(DbRaceResult.race).order_by(desc(DbRace.number)).all()
            ]

        return self._all_race_results

    def all_race_guesses(self) -> List[RaceGuess]:
        """
        Returns a list of all race guesses (of enabled users).
        """
        if self._all_race_guesses is None:
            self._all_race_guesses = [
                RaceGuess.from_db_race_guess(db_race_guess)
                for db_race_guess in db.session.query(DbRaceGuess).join(DbRaceGuess.user).filter_by(enabled=True).all()  # Ignore disabled users
            ]

        return self._all_race_guesses

    def all_season_guesses(self) -> List[SeasonGuess]:
        """
        Returns a list of all season guesses (of enabled users).
        """
        if self._all_season_guesses is None:
            self._all_season_guesses = [
                SeasonGuess.from_db_season_guess(db_season_guess)
                for db_season_guess in db.session.query(DbSeasonGuess).join(DbSeasonGuess.user).filter_by(enabled=True).all()  # Ignore disabled users
            ]

        return self._all_season_guesses

    def all_races(self) -> List[Race]:
        """
        Returns a list of all races, in descending order (last race first).
        """
        if self._all_races is None:
            self._all_races = [
                Race.from_db_race(db_race)
                for db_race in db.session.query(DbRace).order_by(desc(DbRace.number)).all()
            ]

        return self._all_races

    def all_drivers(self, *, include_none: bool) -> List[Driver]:
        """
        Returns a list of all drivers.
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
        Returns a list of all teams.
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

    #
    # User queries
    #

    @overload
    def user_by(self, *, user_name: str) -> User:
        """
        Tries to obtain the user object for a specific username.
        """
        return self.user_by(user_name=user_name)

    @overload
    def user_by(self, *, user_name: str, ignore: List[str]) -> User | None:
        """
        Tries to obtain the user object for a specific username, but ignores certain usernames.
        """
        return self.user_by(user_name=user_name, ignore=ignore)

    def user_by(self, *, user_name: str, ignore: List[str] | None = None) -> User | None:
        if ignore is None:
            ignore = []

        if len(ignore) > 0 and user_name in ignore:
            return None

        predicate: Callable[[User], bool] = lambda user: user.name == user_name
        return find_single_strict(predicate, self.all_users())

    #
    # Race result queries
    #

    def race_result_by(self, *, race_name: str) -> RaceResult | None:
        """
        Tries to obtain the race result corresponding to a race name.
        """
        predicate: Callable[[RaceResult], bool] = lambda result: result.race.name == race_name
        return find_single_or_none_strict(predicate, self.all_race_results())

    #
    # Race guess queries
    #

    @overload
    def race_guesses_by(self, *, user_name: str) -> List[RaceGuess]:
        """
        Returns a list of all race guesses made by a specific user.
        """
        return self.race_guesses_by(user_name=user_name)

    @overload
    def race_guesses_by(self, *, race_name: str) -> List[RaceGuess]:
        """
        Returns a list of all race guesses made for a specific race.
        """
        return self.race_guesses_by(race_name=race_name)

    @overload
    def race_guesses_by(self, *, user_name: str, race_name: str) -> RaceGuess | None:
        """
        Returns a single race guess by a specific user for a specific race, or None, if this guess doesn't exist.
        """
        return self.race_guesses_by(user_name=user_name, race_name=race_name)

    @overload
    def race_guesses_by(self) -> Dict[str, Dict[str, RaceGuess]]:
        """
        Returns a dictionary that maps race-ids to user-id - guess dictionaries.
        """
        return self.race_guesses_by()

    def race_guesses_by(self, *, user_name: str | None = None, race_name: str | None = None) -> RaceGuess | List[RaceGuess] | Dict[str, Dict[str, RaceGuess]] | None:
        # List of all guesses by a single user
        if user_name is not None and race_name is None:
            predicate: Callable[[RaceGuess], bool] = lambda guess: guess.user.name == user_name
            return find_multiple_strict(predicate, self.all_race_guesses())

        # List of all guesses for a single race
        if user_name is None and race_name is not None:
            predicate: Callable[[RaceGuess], bool] = lambda guess: guess.race.name == race_name
            return find_multiple_strict(predicate, self.all_race_guesses())

        # Guess for a single race by a single user
        if user_name is not None and race_name is not None:
            predicate: Callable[[RaceGuess], bool] = lambda guess: guess.user.name == user_name and guess.race.name == race_name
            return find_single_or_none_strict(predicate, self.all_race_guesses())

        # Dict with all guesses
        if user_name is None and race_name is None:
            guesses_by: Dict[str, Dict[str, RaceGuess]] = dict()
            guess: RaceGuess

            for guess in self.all_race_guesses():
                if guess.race.name not in guesses_by:
                    guesses_by[guess.race.name] = dict()

                guesses_by[guess.race.name][guess.user.name] = guess

            return guesses_by

        raise Exception("race_guesses_by encountered illegal combination of arguments")

    #
    # Season guess queries
    #

    @overload
    def season_guesses_by(self, *, user_name: str) -> SeasonGuess:
        """
        Returns the season guess made by a specific user.
        """
        return self.season_guesses_by(user_name=user_name)

    @overload
    def season_guesses_by(self) -> Dict[str, SeasonGuess]:
        """
        Returns a dictionary of season guesses mapped to usernames.
        """
        return self.season_guesses_by()

    def season_guesses_by(self, *, user_name: str | None = None) -> SeasonGuess | Dict[str, SeasonGuess] | None:
        if user_name is not None:
            predicate: Callable[[SeasonGuess], bool] = lambda guess: guess.user.name == user_name
            return find_single_or_none_strict(predicate, self.all_season_guesses())

        if user_name is None:
            guesses_by: Dict[str, SeasonGuess] = dict()
            guess: SeasonGuess

            for guess in self.all_season_guesses():
                guesses_by[guess.user.name] = guess

            return guesses_by

        raise Exception("season_guesses_by encountered illegal combination of arguments")

    #
    # Team queries
    #

    def none_team(self) -> Team:
        return NONE_TEAM

    #
    # Driver queries
    #

    def none_driver(self) -> Driver:
        return NONE_DRIVER

    @overload
    def drivers_by(self, *, team_name: str) -> List[Driver]:
        """
        Returns a list of all drivers driving for a certain team.
        """
        return self.drivers_by(team_name=team_name)

    @overload
    def drivers_by(self) -> Dict[str, List[Driver]]:
        """
        Returns a dictionary of drivers mapped to team names.
        """
        return self.drivers_by()

    def drivers_by(self, *, team_name: str | None = None) -> List[Driver] | Dict[str, List[Driver]]:
        if team_name is not None:
            predicate: Callable[[Driver], bool] = lambda driver: driver.team.name == team_name
            return find_multiple_strict(predicate, self.all_drivers(include_none=False), 2)

        if team_name is None:
            drivers_by: Dict[str, List[Driver]] = dict()
            driver: Driver
            team: Team

            for team in self.all_teams(include_none=False):
                drivers_by[team.name] = []
            for driver in self.all_drivers(include_none=False):
                drivers_by[driver.team.name] += [driver]

            return drivers_by

        raise Exception("drivers_by encountered illegal combination of arguments")

    #
    # Race queries
    #

    def race_by(self, *, race_name: str) -> Race:
        for race in self.all_races():
            if race.name == race_name:
                return race

        raise Exception(f"Couldn't find race {race_name}")