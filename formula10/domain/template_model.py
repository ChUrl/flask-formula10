from typing import List, Callable
from formula10 import ENABLE_TIMING

from formula10.domain.domain_model import Model
from formula10.domain.model.driver import Driver
from formula10.domain.model.race import Race
from formula10.domain.model.race_result import RaceResult
from formula10.domain.model.user import User
from formula10.database.validation import find_first_else_none, find_multiple_strict, find_single_strict, race_has_started


class TemplateModel(Model):
    """
    This class bundles all data + functionality required from inside a template.
    """

    active_user: User | None = None
    active_result: RaceResult | None = None

    # RIC is excluded, since he didn't drive as many races 2023 as the others
    _wdc_gained_excluded_abbrs: List[str] = ["RIC"]

    def __init__(self, *, active_user_name: str | None, active_result_race_name: str | None):
        Model.__init__(self)

        if active_user_name is not None:
            self.active_user = self.user_by(user_name=active_user_name, ignore=["Everyone"])

        if active_result_race_name is not None:
            self.active_result = self.race_result_by(race_name=active_result_race_name)

    def race_guess_open(self, race: Race) -> bool:
        return not race_has_started(race=race) if ENABLE_TIMING else True

    def season_guess_open(self) -> bool:
        return not race_has_started(race_id=1) if ENABLE_TIMING else True

    def race_result_open(self, race_name: str) -> bool:
        predicate: Callable[[Race], bool] = lambda race: race.name == race_name
        race: Race = find_single_strict(predicate, self.all_races())
        return race_has_started(race_id=race.id) if ENABLE_TIMING else True

    def active_user_name_or_everyone(self) -> str:
        return self.active_user.name if self.active_user is not None else "Everyone"

    def active_user_name_sanitized_or_everyone(self) -> str:
        return self.active_user.name_sanitized if self.active_user is not None else "Everyone"

    def all_users_or_active_user(self) -> List[User]:
        if self.active_user is not None:
            return [self.active_user]

        return self.all_users()

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

    def active_result_race_or_current_race(self) -> Race:
        if self.active_result is not None:
            return self.active_result.race
        elif self.current_race is not None:
            return self.current_race
        else:
            return self.all_races()[0]

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

    def all_drivers_or_active_result_standing_drivers(self) -> List[Driver]:
        return self.active_result.ordered_standing_list() if self.active_result is not None else self.all_drivers(include_none=False)

    def drivers_for_wdc_gained(self) -> List[Driver]:
        predicate: Callable[[Driver], bool] = lambda driver: driver.abbr not in self._wdc_gained_excluded_abbrs
        return find_multiple_strict(predicate, self.all_drivers(include_none=False))
