from typing import List, Callable, Dict, overload
from sqlalchemy import desc

from formula10.database.model.driver import Driver
from formula10.database.model.race import Race
from formula10.database.model.race_guess import RaceGuess
from formula10.database.model.race_result import RaceResult
from formula10.database.model.season_guess import SeasonGuess
from formula10.database.model.team import Team
from formula10.database.model.user import User
from formula10.database.validation_util import find_first_or_none, find_multiple, find_single, find_single_or_none
from formula10 import db


# This could also be moved to database_utils (at least partially), but I though the template should cache the database responses
class TemplateModel:
    """
    This class bundles all data required from inside a template.
    """

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
            self._all_users = db.session.query(User).all()

        return self._all_users

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
        return find_single(predicate, self.all_users())

    def all_race_results(self) -> List[RaceResult]:
        """
        Returns a list of all race results in the database, in descending order (most recent first).
        """
        if self._all_race_results is None:
            self._all_race_results = db.session.query(RaceResult).join(RaceResult.race).order_by(desc(Race.number)).all()

        return self._all_race_results

    def race_result_by(self, *, race_name: str) -> RaceResult | None:
        """
        Tries to obtain the race result corresponding to a race name.
        """
        predicate: Callable[[RaceResult], bool] = lambda result: result.race.name == race_name
        return find_single_or_none(predicate, self.all_race_results())

    def all_race_guesses(self) -> List[RaceGuess]:
        """
        Returns a list of all race guesses in the database.
        """
        if self._all_race_guesses is None:
            self._all_race_guesses = db.session.query(RaceGuess).all()

        return self._all_race_guesses

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
            predicate: Callable[[RaceGuess], bool] = lambda guess: guess.user_name == user_name
            return find_multiple(predicate, self.all_race_guesses())

        # List of all guesses for a single race
        if user_name is None and race_name is not None:
            predicate: Callable[[RaceGuess], bool] = lambda guess: guess.race_name == race_name
            return find_multiple(predicate, self.all_race_guesses())

        # Guess for a single race by a single user
        if user_name is not None and race_name is not None:
            predicate: Callable[[RaceGuess], bool] = lambda guess: guess.user_name == user_name and guess.race_name == race_name
            return find_single_or_none(predicate, self.all_race_guesses())

        # Dict with all guesses
        if user_name is None and race_name is None:
            guesses_by: Dict[str, Dict[str, RaceGuess]] = dict()
            guess: RaceGuess

            for guess in self.all_race_guesses():
                if guess.race_name not in guesses_by:
                    guesses_by[guess.race_name] = dict()

                guesses_by[guess.race_name][guess.user_name] = guess

            return guesses_by

        raise Exception("race_guesses_by encountered illegal combination of arguments")

    def all_season_guesses(self) -> List[SeasonGuess]:
        if self._all_season_guesses is None:
            self._all_season_guesses = db.session.query(SeasonGuess).all()

        return self._all_season_guesses

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
            predicate: Callable[[SeasonGuess], bool] = lambda guess: guess.user_name == user_name
            return find_single_or_none(predicate, self.all_season_guesses())

        if user_name is None:
            guesses_by: Dict[str, SeasonGuess] = dict()
            guess: SeasonGuess

            for guess in self.all_season_guesses():
                guesses_by[guess.user_name] = guess

            return guesses_by

        raise Exception("season_guesses_by encountered illegal combination of arguments")

    def all_races(self) -> List[Race]:
        """
        Returns a list of all races in the database.
        """
        if self._all_races is None:
            self._all_races = db.session.query(Race).order_by(desc(Race.number)).all()

        return self._all_races

    def first_race_without_result(self) -> Race | None:
        """
        Returns the first race-object with no associated race result.
        """
        results: List[RaceResult] = self.all_race_results()
        if len(results) == 0:
            return self.all_races()[-1]  # all_races is sorted descending by number

        most_recent_result: RaceResult = results[0]
        predicate: Callable[[Race], bool] = lambda race: race.number == most_recent_result.race.number + 1

        return find_first_or_none(predicate, self.all_races())

    def all_teams(self) -> List[Team]:
        """
        Returns a list of all teams in the database.
        """
        if self._all_teams is None:
            self._all_teams = db.session.query(Team).all()

        return self._all_teams

    def all_drivers(self) -> List[Driver]:
        """
        Returns a list of all drivers in the database, including the NONE driver.
        """
        if self._all_drivers is None:
            self._all_drivers = db.session.query(Driver).all()

        return self._all_drivers

    def all_drivers_except_none(self) -> List[Driver]:
        """
        Returns a list of all drivers in the database, excluding the NONE driver.
        """
        predicate: Callable[[Driver], bool] = lambda driver: driver.name != "None"
        return find_multiple(predicate, self.all_drivers())

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
            return find_multiple(predicate, self.all_drivers_except_none(), 2)

        if team_name is None:
            drivers_by: Dict[str, List[Driver]] = dict()
            driver: Driver
            team: Team

            for team in self.all_teams():
                drivers_by[team.name] = []
            for driver in self.all_drivers_except_none():
                drivers_by[driver.team.name] += [driver]

            return drivers_by

        raise Exception("drivers_by encountered illegal combination of arguments")
