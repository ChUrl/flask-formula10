from typing import Callable, Dict, List, overload
from sqlalchemy import desc

from formula10.database.model.db_driver import DbDriver
from formula10.database.model.db_race import DbRace
from formula10.database.model.db_race_guess import DbRaceGuess
from formula10.database.model.db_race_result import DbRaceResult
from formula10.database.model.db_season_guess import DbSeasonGuess
from formula10.database.model.db_season_guess_result import DbSeasonGuessResult
from formula10.database.model.db_team import DbTeam
from formula10.database.model.db_user import DbUser
from formula10.database.validation import find_multiple_strict, find_single_or_none_strict, find_single_strict, find_atleast_strict
from formula10.domain.model.driver import NONE_DRIVER, Driver
from formula10.domain.model.race import Race
from formula10.domain.model.race_guess import RaceGuess
from formula10.domain.model.race_result import RaceResult
from formula10.domain.model.season_guess import SeasonGuess
from formula10.domain.model.season_guess_result import SeasonGuessResult
from formula10.domain.model.team import NONE_TEAM, Team
from formula10.domain.model.user import User
from formula10 import db, cache


class Model:
    @staticmethod
    @cache.cached(timeout=None, key_prefix="domain_all_users") # Clear when adding/deleting users
    def all_users() -> List[User]:
        """
        Returns a list of all enabled users.
        """
        db_users = db.session.query(DbUser).filter_by(enabled=True).all()
        return [User.from_db_user(db_user) for db_user in db_users]

    @staticmethod
    @cache.cached(timeout=None, key_prefix="domain_all_race_results") # Clear when adding/updating results
    def all_race_results() -> List[RaceResult]:
        """
        Returns a list of all race results, in descending order (most recent first).
        """
        db_race_results = db.session.query(DbRaceResult).join(DbRaceResult.race).order_by(desc("number")).all()
        return [RaceResult.from_db_race_result(db_race_result) for db_race_result in db_race_results]

    @staticmethod
    @cache.cached(timeout=None, key_prefix="domain_all_race_guesses") # Clear when adding/updating race guesses or users
    def all_race_guesses() -> List[RaceGuess]:
        """
        Returns a list of all race guesses (of enabled users).
        """
        db_race_guesses = db.session.query(DbRaceGuess).join(DbRaceGuess.user).filter_by(enabled=True).all()
        return [RaceGuess.from_db_race_guess(db_race_guess) for db_race_guess in db_race_guesses]

    @staticmethod
    @cache.cached(timeout=None, key_prefix="domain_all_season_guesses") # Clear when adding/updating season guesses or users
    def all_season_guesses() -> List[SeasonGuess]:
        """
        Returns a list of all season guesses (of enabled users).
        """
        db_season_guesses = db.session.query(DbSeasonGuess).join(DbSeasonGuess.user).filter_by(enabled=True).all()
        return [SeasonGuess.from_db_season_guess(db_season_guess) for db_season_guess in db_season_guesses]

    @staticmethod
    @cache.cached(timeout=None, key_prefix="domain_all_season_guess_results") # No cleanup, bc entered manually
    def all_season_guess_results() -> List[SeasonGuessResult]:
        """
        Returns a list of all season guess results (of enabled users).
        """
        db_season_guess_results = db.session.query(DbSeasonGuessResult).join(DbSeasonGuessResult.user).filter_by(enabled=True).all()
        return [SeasonGuessResult.from_db_season_guess_result(db_season_guess_result) for db_season_guess_result in db_season_guess_results]

    @staticmethod
    @cache.cached(timeout=None, key_prefix="domain_all_races") # No cleanup, bc entered manually
    def all_races() -> List[Race]:
        """
        Returns a list of all races, in descending order (last race first).
        """
        db_races = db.session.query(DbRace).order_by(desc("number")).all()
        return [Race.from_db_race(db_race) for db_race in db_races]

    @staticmethod
    @cache.memoize(timeout=None) # No cleanup, bc entered manually
    def all_drivers(*, include_none: bool, include_inactive: bool) -> List[Driver]:
        """
        Returns a list of all active drivers.
        """
        db_drivers = db.session.query(DbDriver).all()
        drivers = [Driver.from_db_driver(db_driver) for db_driver in db_drivers]

        if not include_inactive:
            predicate: Callable[[Driver], bool] = lambda driver: driver.active
            drivers = find_multiple_strict(predicate, drivers)

        if not include_none:
            predicate: Callable[[Driver], bool] = lambda driver: driver != NONE_DRIVER
            drivers = find_multiple_strict(predicate, drivers)

        return drivers

    @staticmethod
    @cache.memoize(timeout=None) # No cleanup, bc entered manually
    def all_teams(*, include_none: bool) -> List[Team]:
        """
        Returns a list of all teams.
        """
        db_teams = db.session.query(DbTeam).all()
        teams = [Team.from_db_team(db_team) for db_team in db_teams]

        if not include_none:
            predicate: Callable[[Team], bool] = lambda team: team != NONE_TEAM
            return find_multiple_strict(predicate, teams)

        return teams

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

    @cache.memoize(timeout=None, args_to_ignore=["self"]) # Cleanup when adding/updating race guesses or users
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
    def season_guesses_by(self, *, user_name: str) -> SeasonGuess | None:
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

    @cache.memoize(timeout=None, args_to_ignore=["self"]) # Cleanup when adding/updating season guesses or users
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
    # Season guess result queries
    #

    def season_guess_result_by(self, *, user_name: str) -> SeasonGuessResult | None:
        predicate: Callable[[SeasonGuessResult], bool] = lambda guess: guess.user.name == user_name
        return find_single_or_none_strict(predicate, self.all_season_guess_results())

    #
    # Team queries
    #

    @staticmethod
    def none_team() -> Team:
        return NONE_TEAM

    #
    # Driver queries
    #

    @staticmethod
    def none_driver() -> Driver:
        return NONE_DRIVER

    @overload
    def drivers_by(self, *, team_name: str, include_inactive: bool) -> List[Driver]:
        """
        Returns a list of all drivers driving for a certain team.
        """
        return self.drivers_by(team_name=team_name, include_inactive=include_inactive)

    @overload
    def drivers_by(self, *, include_inactive: bool) -> Dict[str, List[Driver]]:
        """
        Returns a dictionary of drivers mapped to team names.
        """
        return self.drivers_by(include_inactive=include_inactive)

    @cache.memoize(timeout=None, args_to_ignore=["self"]) # No Cleanup, data added manually
    def drivers_by(self, *, team_name: str | None = None, include_inactive: bool) -> List[Driver] | Dict[str, List[Driver]]:
        if team_name is not None:
            predicate: Callable[[Driver], bool] = lambda driver: driver.team.name == team_name

            if include_inactive:
                return find_atleast_strict(predicate, self.all_drivers(include_none=False, include_inactive=True), 2)
            else:
                return find_multiple_strict(predicate, self.all_drivers(include_none=False, include_inactive=False), 2)

        if team_name is None:
            drivers_by: Dict[str, List[Driver]] = dict()
            driver: Driver
            team: Team

            for team in self.all_teams(include_none=False):
                drivers_by[team.name] = []
            for driver in self.all_drivers(include_none=False, include_inactive=include_inactive):
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