from typing import List, Callable, Dict, overload

from formula10.domain.domain_model import Model
from formula10.domain.model.driver import NONE_DRIVER, Driver
from formula10.domain.model.race import Race
from formula10.domain.model.race_guess import RaceGuess
from formula10.domain.model.race_result import RaceResult
from formula10.domain.model.season_guess import SeasonGuess
from formula10.domain.model.team import NONE_TEAM, Team
from formula10.domain.model.user import User
from formula10.database.validation import find_first_else_none, find_multiple_strict, find_single_strict, find_single_or_none_strict, race_has_started


class TemplateModel(Model):
    """
    This class bundles all data required from inside a template.
    """

    active_user: User | None = None
    active_result: RaceResult | None = None

    # RIC is excluded, since he didn't drive as many races 2023 as the others
    _wdc_gained_excluded_abbrs: List[str] = ["RIC"]

    def __init__(self, *, active_user_name: str | None, active_result_race_name: str | None):
        if active_user_name is not None:
            self.active_user = self.user_by(user_name=active_user_name, ignore=["Everyone"])

        if active_result_race_name is not None:
            self.active_result = self.race_result_by(race_name=active_result_race_name)

    def race_guess_open(self, race: Race) -> bool:
        return not race_has_started(race=race)

    def season_guess_open(self) -> bool:
        return not race_has_started(race_name="Bahrain")

    def active_user_name_or_everyone(self) -> str:
        return self.active_user.name if self.active_user is not None else "Everyone"

    def active_user_name_sanitized_or_everyone(self) -> str:
        return self.active_user.name_sanitized if self.active_user is not None else "Everyone"

    def all_users_or_active_user(self) -> List[User]:
        if self.active_user is not None:
            return [self.active_user]

        return self.all_users()

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

    def race_result_by(self, *, race_name: str) -> RaceResult | None:
        """
        Tries to obtain the race result corresponding to a race name.
        """
        predicate: Callable[[RaceResult], bool] = lambda result: result.race.name == race_name
        return find_single_or_none_strict(predicate, self.all_race_results())

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

    def first_race_without_result(self) -> Race | None:
        """
        Returns the first race-object with no associated race result.
        """
        results: List[RaceResult] = self.all_race_results()
        if len(results) == 0:
            return self.all_races()[-1]  # all_races is sorted descending by number

        most_recent_result: RaceResult = results[0]
        predicate: Callable[[Race], bool] = lambda race: race.number == most_recent_result.race.number + 1

        return find_first_else_none(predicate, self.all_races())

    @property
    def current_race(self) -> Race | None:
        return self.first_race_without_result()

    def active_result_race_name_or_current_race_name(self) -> str:
        if self.active_result is not None:
            return self.active_result.race.name
        elif self.current_race is not None:
            return self.current_race.name
        else:
            return self.all_races()[0].name

    def active_result_race_name_or_current_race_name_sanitized(self) -> str:
        if self.active_result is not None:
            return self.active_result.race.name_sanitized
        elif self.current_race is not None:
            return self.current_race.name_sanitized
        else:
            return self.all_races()[0].name_sanitized

    def none_team(self) -> Team:
        return NONE_TEAM

    def all_drivers_or_active_result_standing_drivers(self) -> List[Driver]:
        return self.active_result.ordered_standing_list() if self.active_result is not None else self.all_drivers(include_none=False)

    def drivers_for_wdc_gained(self) -> List[Driver]:
        predicate: Callable[[Driver], bool] = lambda driver: driver.abbr not in self._wdc_gained_excluded_abbrs
        return find_multiple_strict(predicate, self.all_drivers(include_none=False))

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
