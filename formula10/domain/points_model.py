import json
from typing import Any, Callable, Dict, List, overload, Tuple
import numpy as np

from formula10 import cache
from formula10.domain.domain_model import Model
from formula10.domain.model.driver import NONE_DRIVER, Driver
from formula10.domain.model.race_guess import RaceGuess
from formula10.domain.model.race_result import RaceResult
from formula10.domain.model.season_guess import SeasonGuess
from formula10.domain.model.season_guess_result import SeasonGuessResult
from formula10.domain.model.team import Team
from formula10.domain.model.user import User
from formula10.database.validation import find_single_or_none_strict

# Guess points

RACE_GUESS_OFFSET_POINTS: Dict[int, int] = {3: 1, 2: 3, 1: 6, 0: 10}
RACE_GUESS_DNF_POINTS: int = 10
SEASON_GUESS_HOT_TAKE_POINTS: int = 10
SEASON_GUESS_P2_POINTS: int = 10
SEASON_GUESS_OVERTAKES_POINTS: int = 10
SEASON_GUESS_DNF_POINTS: int = 10
SEASON_GUESS_GAINED_POINTS: int = 10
SEASON_GUESS_LOST_POINTS: int = 10
SEASON_GUESS_TEAMWINNER_CORRECT_POINTS: int = 3
SEASON_GUESS_TEAMWINNER_FALSE_POINTS: int = -3
SEASON_GUESS_PODIUMS_CORRECT_POINTS: int = 3
SEASON_GUESS_PODIUMS_FALSE_POINTS: int = -2

# Driver points

DRIVER_RACE_POINTS: Dict[int, int] = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1,
}
DRIVER_SPRINT_POINTS: Dict[int, int] = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
DRIVER_FASTEST_LAP_POINTS: int = 1

# Last season results

WDC_STANDING_2023: Dict[str, int] = {
    "Max Verstappen": 1,
    "Sergio Perez": 2,
    "Lewis Hamilton": 3,
    "Fernando Alonso": 4,
    "Charles Leclerc": 5,
    "Lando Norris": 6,
    "Carlos Sainz": 7,
    "George Russell": 8,
    "Oscar Piastri": 9,
    "Lance Stroll": 10,
    "Pierre Gasly": 11,
    "Esteban Ocon": 12,
    "Alexander Albon": 13,
    "Yuki Tsunoda": 14,
    "Valtteri Bottas": 15,
    "Nico Hulkenberg": 16,
    "Daniel Ricciardo": 17,
    "Zhou Guanyu": 18,
    "Kevin Magnussen": 19,
    "Logan Sargeant": 21,
}

WCC_STANDING_2023: Dict[str, int] = {
    "Red Bull": 1,
    "Mercedes": 2,
    "Ferrari": 3,
    "McLaren": 4,
    "Aston Martin": 5,
    "Alpine": 6,
    "Williams": 7,
    "VCARB": 8,
    "Sauber": 9,
    "Haas": 10,
}

# In case a substitute driver is driving, those points have to be subtracted from the actual driver
# (Driver_ID, Race_ID, Points)
WDC_SUBSTITUTE_POINTS: List[Tuple[int, int, int]] = [
    (15, 2, 6), # Bearman raced for Sainz in Saudi Arabia
    (8, 17, 1), # Bearman raced for Magnussen in Azerbaijan
]

def standing_points(race_guess: RaceGuess, race_result: RaceResult) -> int:
    guessed_driver_position: int | None = race_result.driver_standing_position(
        driver=race_guess.pxx_guess
    )
    if guessed_driver_position is None:
        return 0

    position_offset: int = abs(guessed_driver_position - race_guess.race.place_to_guess)
    if position_offset not in RACE_GUESS_OFFSET_POINTS:
        return 0

    return RACE_GUESS_OFFSET_POINTS[position_offset]


def dnf_points(race_guess: RaceGuess, race_result: RaceResult) -> int:
    if race_guess.dnf_guess in race_result.initial_dnf:
        return RACE_GUESS_DNF_POINTS

    if race_guess.dnf_guess == NONE_DRIVER and len(race_result.initial_dnf) == 0:
        return RACE_GUESS_DNF_POINTS

    return 0


def substitute_points(driver: Driver, race_number: int) -> int:
    predicate: Callable[[Tuple[int, int, int]], bool] = lambda substitution: driver.id == substitution[0] and race_number == substitution[1]
    substitution: Tuple[int, int, int] = find_single_or_none_strict(predicate, WDC_SUBSTITUTE_POINTS)

    if substitution is not None:
        return substitution[2]
    else:
        return 0


class PointsModel(Model):
    """
    This class bundles all data + functionality required to do points calculations.
    """

    def __init__(self):
        Model.__init__(self)

    @cache.cached(
        timeout=None, key_prefix="points_points_per_step"
    )  # Clear when adding/updating race results or users
    def points_per_step(self) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing points per race for each user.
        """
        points_per_step = dict()
        for user in self.all_users():
            points_per_step[user.name] = [0] * (
                    len(self.all_races()) + 1
            )  # Start at index 1, like the race numbers

        for race_guess in self.all_race_guesses():
            user_name: str = race_guess.user.name
            race_number: int = race_guess.race.number
            race_result: RaceResult | None = self.race_result_by(
                race_name=race_guess.race.name
            )

            if race_result is None:
                continue

            points_per_step[user_name][race_number] = standing_points(
                race_guess, race_result
            ) + dnf_points(race_guess, race_result)

        return points_per_step

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Clear when adding/updating race results
    def driver_points_per_step(self, *, include_inactive: bool) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing points per race for each driver.
        """
        driver_points_per_step = dict()
        for driver in self.all_drivers(
                include_none=False, include_inactive=include_inactive
        ):
            driver_points_per_step[driver.name] = [0] * (
                    len(self.all_races()) + 1
            )  # Start at index 1, like the race numbers

        for race_result in self.all_race_results():
            race_number: int = race_result.race.number

            for position, driver in race_result.standing.items():
                driver_points_per_step[driver.name][race_number] = (
                    DRIVER_RACE_POINTS[int(position)]
                    if int(position) in DRIVER_RACE_POINTS
                    else 0
                )
                driver_points_per_step[driver.name][race_number] += (
                    DRIVER_FASTEST_LAP_POINTS
                    if race_result.fastest_lap_driver == driver
                    and int(position) <= 10
                    else 0
                )
                driver_points_per_step[driver.name][race_number] -= substitute_points(driver, race_number)

            for position, driver in race_result.sprint_standing.items():
                driver_name: str = driver.name

                driver_points_per_step[driver_name][race_number] += (
                    DRIVER_SPRINT_POINTS[int(position)]
                    if int(position) in DRIVER_SPRINT_POINTS
                    else 0
                )

        return driver_points_per_step

    @cache.cached(timeout=None, key_prefix="points_team_points_per_step")
    def team_points_per_step(self) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing points per race for each team.
        """
        team_points_per_step = dict()
        for team in self.all_teams(include_none=False):
            team_points_per_step[team.name] = [0] * (
                    len(self.all_races()) + 1
            )  # Start at index 1, like the race numbers

        for race_result in self.all_race_results():
            for driver in race_result.standing.values():
                team_name: str = driver.team.name
                race_number: int = race_result.race.number

                team_points_per_step[team_name][
                    race_number
                ] += self.driver_points_per_step(include_inactive=True)[driver.name][
                    race_number
                ]

        return team_points_per_step

    @cache.cached(timeout=None, key_prefix="points_dnfs")
    def dnfs(self) -> Dict[str, int]:
        dnfs = dict()

        for driver in self.all_drivers(include_none=False, include_inactive=True):
            dnfs[driver.name] = 0

        for race_result in self.all_race_results():
            for driver in race_result.all_dnfs:
                dnfs[driver.name] += 1

            for driver in race_result.sprint_dnfs:
                dnfs[driver.name] += 1

        return dnfs

    #
    # Driver stats
    #

    @cache.cached(
        timeout=None, key_prefix="points_driver_points_per_step_cumulative"
    )  # Cleanup when adding/updating race results
    def driver_points_per_step_cumulative(self) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing cumulative points per race for each driver.
        """
        points_per_step_cumulative: Dict[str, List[int]] = dict()
        for driver_name, points in self.driver_points_per_step(
                include_inactive=True
        ).items():
            points_per_step_cumulative[driver_name] = np.cumsum(points).tolist()

        return points_per_step_cumulative

    @overload
    def driver_points_by(
            self, *, driver_name: str, include_inactive: bool
    ) -> List[int]:
        """
        Returns a list of points per race for a specific driver.
        """
        return self.driver_points_by(
            driver_name=driver_name, include_inactive=include_inactive
        )

    @overload
    def driver_points_by(
            self, *, race_name: str, include_inactive: bool
    ) -> Dict[str, int]:
        """
        Returns a dictionary of points per driver for a specific race.
        """
        return self.driver_points_by(
            race_name=race_name, include_inactive=include_inactive
        )

    @overload
    def driver_points_by(
            self, *, driver_name: str, race_name: str, include_inactive: bool
    ) -> int:
        """
        Returns the points for a specific race for a specific driver.
        """
        return self.driver_points_by(
            driver_name=driver_name,
            race_name=race_name,
            include_inactive=include_inactive,
        )

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def driver_points_by(
            self,
            *,
            driver_name: str | None = None,
            race_name: str | None = None,
            include_inactive: bool
    ) -> List[int] | Dict[str, int] | int:
        if driver_name is not None and race_name is None:
            return self.driver_points_per_step(include_inactive=include_inactive)[
                driver_name
            ]

        if driver_name is None and race_name is not None:
            race_number: int = self.race_by(race_name=race_name).number
            points_by_race: Dict[str, int] = dict()

            for _driver_name, points in self.driver_points_per_step(
                    include_inactive=include_inactive
            ).items():
                points_by_race[_driver_name] = points[race_number]

            return points_by_race

        if driver_name is not None and race_name is not None:
            race_number: int = self.race_by(race_name=race_name).number

            return self.driver_points_per_step(include_inactive=include_inactive)[
                driver_name
            ][race_number]

        raise Exception("driver_points_by received an illegal combination of arguments")

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def total_driver_points_by(self, driver_name: str) -> int:
        return sum(
            self.driver_points_by(driver_name=driver_name, include_inactive=True)
        )

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def drivers_sorted_by_points(self, *, include_inactive: bool) -> List[Driver]:
        comparator: Callable[[Driver], int] = (
            lambda driver: self.total_driver_points_by(driver.name)
        )
        return sorted(
            self.all_drivers(include_none=False, include_inactive=include_inactive),
            key=comparator,
            reverse=True,
        )

    @cache.cached(
        timeout=None, key_prefix="points_wdc_standing_by_position"
    )  # Cleanup when adding/updating race results
    def wdc_standing_by_position(self) -> Dict[int, List[str]]:
        standing: Dict[int, List[str]] = dict()

        for position in range(
                1, len(self.all_drivers(include_none=False, include_inactive=True)) + 1
        ):
            standing[position] = list()

        position: int = 1
        last_points: int = 0

        for driver in self.drivers_sorted_by_points(include_inactive=True):
            points: int = self.total_driver_points_by(driver.name)
            if points < last_points:
                # If multiple drivers have equal points, a place is shared.
                # In this case, the next driver does not occupy the immediate next position.
                position += len(standing[position])

            standing[position].append(driver.name)
            last_points = points

        return standing

    @cache.cached(
        timeout=None, key_prefix="points_wdc_standing_by_driver"
    )  # Cleanup when adding/updating race results
    def wdc_standing_by_driver(self) -> Dict[str, int]:
        standing: Dict[str, int] = dict()

        position: int = 1
        last_points: int = 0

        for driver in self.drivers_sorted_by_points(include_inactive=True):
            points: int = self.total_driver_points_by(driver.name)
            if points < last_points:
                drivers_with_this_position = 0
                for _driver, _position in standing.items():
                    if _position == position:
                        drivers_with_this_position += 1

                # If multiple drivers have equal points, a place is shared.
                # In this case, the next driver does not occupy the immediate next position.
                position += drivers_with_this_position

            standing[driver.name] = position
            last_points = points

        return standing

    def wdc_diff_2023_by(self, driver_name: str) -> int:
        if not driver_name in WDC_STANDING_2023:
            return 0

        return (
                WDC_STANDING_2023[driver_name] - self.wdc_standing_by_driver()[driver_name]
        )

    @cache.cached(
        timeout=None, key_prefix="points_most_dnf_names"
    )  # Cleanup when adding/updating race results
    def most_dnf_names(self) -> List[str]:
        dnf_names: List[str] = list()
        most_dnfs: int = 0

        for dnfs in self.dnfs().values():
            if dnfs > most_dnfs:
                most_dnfs = dnfs

        for driver_name, dnfs in self.dnfs().items():
            if dnfs == most_dnfs:
                dnf_names.append(driver_name)

        return dnf_names

    @cache.cached(
        timeout=None, key_prefix="points_most_gained_names"
    )  # Cleanup when adding/updating race results
    def most_gained_names(self) -> List[str]:
        most_gained_names: List[str] = list()
        most_gained: int = 0

        for driver in self.all_drivers(include_none=False, include_inactive=True):
            gained: int = self.wdc_diff_2023_by(driver.name)

            if gained > most_gained:
                most_gained = gained

        for driver in self.all_drivers(include_none=False, include_inactive=True):
            gained: int = self.wdc_diff_2023_by(driver.name)

            if gained == most_gained:
                most_gained_names.append(driver.name)

        return most_gained_names

    @cache.cached(
        timeout=None, key_prefix="points_most_lost_names"
    )  # Cleanup when adding/updating race results
    def most_lost_names(self) -> List[str]:
        most_lost_names: List[str] = list()
        most_lost: int = 100

        for driver in self.all_drivers(include_none=False, include_inactive=True):
            lost: int = self.wdc_diff_2023_by(driver.name)

            if lost < most_lost:
                most_lost = lost

        for driver in self.all_drivers(include_none=False, include_inactive=True):
            lost: int = self.wdc_diff_2023_by(driver.name)

            if lost == most_lost:
                most_lost_names.append(driver.name)

        return most_lost_names

    #
    # Team points
    #

    @cache.cached(
        timeout=None, key_prefix="points_team_points_per_step_cumulative"
    )  # Cleanup when adding/updating race results
    def team_points_per_step_cumulative(self) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing cumulative points per race for each team.
        """
        points_per_step_cumulative: Dict[str, List[int]] = dict()
        for team_name, points in self.team_points_per_step().items():
            points_per_step_cumulative[team_name] = np.cumsum(points).tolist()

        return points_per_step_cumulative

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def total_team_points_by(self, team_name: str) -> int:
        teammates: List[Driver] = self.drivers_by(
            team_name=team_name, include_inactive=True
        )
        return sum(
            sum(self.driver_points_by(driver_name=teammate.name, include_inactive=True))
            for teammate in teammates
        )

    @cache.cached(
        timeout=None, key_prefix="points_teams_sorted_by_points"
    )  # Cleanup when adding/updating race results
    def teams_sorted_by_points(self) -> List[Team]:
        comparator: Callable[[Team], int] = lambda team: self.total_team_points_by(
            team.name
        )
        return sorted(self.all_teams(include_none=False), key=comparator, reverse=True)

    @cache.cached(
        timeout=None, key_prefix="points_wcc_standing_by_position"
    )  # Cleanup when adding/updating race results
    def wcc_standing_by_position(self) -> Dict[int, List[str]]:
        standing: Dict[int, List[str]] = dict()

        for position in range(1, len(self.all_teams(include_none=False)) + 1):
            standing[position] = list()

        position: int = 1
        last_points: int = 0

        for team in self.teams_sorted_by_points():
            points: int = self.total_team_points_by(team.name)
            if points < last_points:
                # If multiple teams have equal points, a place is shared.
                # In this case, the next team does not occupy the immediate next position.
                position += len(standing[position])

            standing[position].append(team.name)
            last_points = points

        return standing

    @cache.cached(
        timeout=None, key_prefix="points_wcc_standing_by_team"
    )  # Cleanup when adding/updating race results
    def wcc_standing_by_team(self) -> Dict[str, int]:
        standing: Dict[str, int] = dict()

        position: int = 1
        last_points: int = 0

        for team in self.teams_sorted_by_points():
            points: int = self.total_team_points_by(team.name)
            if points < last_points:
                teams_with_this_position = 0
                for _team, _position in standing.items():
                    if _position == position:
                        teams_with_this_position += 1

                # If multiple teams have equal points, a place is shared.
                # In this case, the next team does not occupy the immediate next position.
                position += teams_with_this_position

            standing[team.name] = position
            last_points = points

        return standing

    def wcc_diff_2023_by(self, team_name: str) -> int:
        return WCC_STANDING_2023[team_name] - self.wcc_standing_by_team()[team_name]

    #
    # User stats
    #

    def points_per_step_cumulative(self) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing cumulative points per race for each user.
        """
        points_per_step_cumulative: Dict[str, List[int]] = dict()
        for user_name, points in self.points_per_step().items():
            points_per_step_cumulative[user_name] = np.cumsum(points).tolist()

        return points_per_step_cumulative

    @overload
    def points_by(self, *, user_name: str) -> List[int]:
        """
        Returns a list of points per race for a specific user.
        """
        return self.points_by(user_name=user_name)

    @overload
    def points_by(self, *, race_name: str) -> Dict[str, int]:
        """
        Returns a dictionary of points per user for a specific race.
        """
        return self.points_by(race_name=race_name)

    @overload
    def points_by(self, *, user_name: str, race_name: str) -> int:
        """
        Returns the points for a specific race for a specific user.
        """
        return self.points_by(user_name=user_name, race_name=race_name)

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results or users
    def points_by(
            self, *, user_name: str | None = None, race_name: str | None = None
    ) -> List[int] | Dict[str, int] | int:
        if user_name is not None and race_name is None:
            return self.points_per_step()[user_name]

        if user_name is None and race_name is not None:
            race_number: int = self.race_by(race_name=race_name).number
            points_by_race: Dict[str, int] = dict()

            for _user_name, points in self.points_per_step().items():
                points_by_race[_user_name] = points[race_number]

            return points_by_race

        if user_name is not None and race_name is not None:
            race_number: int = self.race_by(race_name=race_name).number

            return self.points_per_step()[user_name][race_number]

        raise Exception("points_by received an illegal combination of arguments")

    def season_points_by(self, *, user_name: str) -> int:
        """
        Returns the number of points from seasonguesses for a specific user.
        """
        big_picks = (int(self.hot_take_correct(user_name=user_name)) * 10
                     + int(self.p2_constructor_correct(user_name=user_name)) * 10
                     + int(self.overtakes_correct(user_name=user_name)) * 10
                     + int(self.dnfs_correct(user_name=user_name)) * 10
                     + int(self.most_gained_correct(user_name=user_name)) * 10
                     + int(self.most_lost_correct(user_name=user_name)) * 10)

        small_picks = 0
        guess: SeasonGuess = self.season_guesses_by(user_name=user_name)

        for driver in guess.team_winners:
            if self.is_team_winner(driver):
                small_picks += 3
            else:
                small_picks -= 3

        # NOTE: Not picked drivers that had a podium are also wrong
        for driver in self.all_drivers(include_none=False, include_inactive=True):
            if driver in guess.podiums and self.has_podium(driver):
                small_picks += 3
            elif driver in guess.podiums and not self.has_podium(driver):
                small_picks -=2
            elif driver not in guess.podiums and self.has_podium(driver):
                small_picks -=2

        return big_picks + small_picks

    def total_points_by(self, *, user_name: str, include_season: bool) -> int:
        """
        Returns the total number of points for a specific user.
        """
        if include_season:
            return sum(self.points_by(user_name=user_name)) + self.season_points_by(user_name=user_name)
        else:
            return sum(self.points_by(user_name=user_name))

    def users_sorted_by_points(self, *, include_season: bool) -> List[User]:
        """
        Returns the list of users, sorted by their points from race guesses (in descending order).
        """
        comparator: Callable[[User], int] = lambda user: self.total_points_by(user_name=user.name, include_season=include_season)
        return sorted(self.all_users(), key=comparator, reverse=True)

    @cache.cached(
        timeout=None, key_prefix="points_user_standing"
    )  # Cleanup when adding/updating race results or users
    def user_standing(self, *, include_season: bool) -> Dict[str, int]:
        standing: Dict[str, int] = dict()

        position: int = 1
        last_points: int = 0

        for user in self.users_sorted_by_points(include_season=include_season):
            if self.total_points_by(user_name=user.name, include_season=include_season) < last_points:
                users_with_this_position = 0
                for _user, _position in standing.items():
                    if _position == position:
                        users_with_this_position += 1

                # If multiple users have equal points, a place is shared.
                # In this case, the next user does not occupy the immediate next position.
                position += users_with_this_position

            standing[user.name] = position

            last_points = self.total_points_by(user_name=user.name, include_season=include_season)

        return standing

    def picks_count(self, user_name: str) -> int:
        # Treat standing + dnf picks separately
        return len(self.race_guesses_by(user_name=user_name)) * 2

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def picks_with_points_count(self, user_name: str) -> int:
        count: int = 0

        for race_guess in self.race_guesses_by(user_name=user_name):
            race_result: RaceResult | None = self.race_result_by(
                race_name=race_guess.race.name
            )
            if race_result is None:
                continue

            if standing_points(race_guess, race_result) > 0:
                count += 1
            if dnf_points(race_guess, race_result) > 0:
                count += 1

        return count

    def points_per_pick(self, user_name: str) -> float:
        if self.picks_count(user_name) == 0:
            return 0.0

        return self.total_points_by(user_name=user_name, include_season=False) / self.picks_count(user_name)

    #
    # Season guess evaluation
    #

    def hot_take_correct(self, user_name: str) -> bool:
        season_guess_result: SeasonGuessResult | None = self.season_guess_result_by(
            user_name=user_name
        )

        return (
            season_guess_result.hot_take_correct
            if season_guess_result is not None
            else False
        )

    def p2_constructor_correct(self, user_name: str) -> bool:
        season_guess: SeasonGuess | None = self.season_guesses_by(user_name=user_name)

        if season_guess is None or season_guess.p2_wcc is None:
            return False

        return season_guess.p2_wcc.name in self.wcc_standing_by_position()[2]

    def overtakes_correct(self, user_name: str) -> bool:
        season_guess_result: SeasonGuessResult | None = self.season_guess_result_by(
            user_name=user_name
        )

        return (
            season_guess_result.overtakes_correct
            if season_guess_result is not None
            else False
        )

    def dnfs_correct(self, user_name: str) -> bool:
        season_guess: SeasonGuess | None = self.season_guesses_by(user_name=user_name)

        if season_guess is None or season_guess.most_dnfs is None:
            return False

        return season_guess.most_dnfs.name in self.most_dnf_names()

    def most_gained_correct(self, user_name: str) -> bool:
        season_guess: SeasonGuess | None = self.season_guesses_by(user_name=user_name)

        if season_guess is None or season_guess.most_wdc_gained is None:
            return False

        return season_guess.most_wdc_gained.name in self.most_gained_names()

    def most_lost_correct(self, user_name: str) -> bool:
        season_guess: SeasonGuess | None = self.season_guesses_by(user_name=user_name)

        if season_guess is None or season_guess.most_wdc_lost is None:
            return False

        return season_guess.most_wdc_lost.name in self.most_lost_names()

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def is_team_winner(self, driver: Driver) -> bool:
        teammates: List[Driver] = self.drivers_by(
            team_name=driver.team.name, include_inactive=True
        )

        # Min - Highest position is the lowest place number
        winner: Driver = min(teammates, key=lambda driver: self.wdc_standing_by_driver()[driver.name])

        return driver == winner

    @cache.memoize(
        timeout=None, args_to_ignore=["self"]
    )  # Cleanup when adding/updating race results
    def has_podium(self, driver: Driver) -> bool:
        for race_result in self.all_race_results():
            position: int | None = race_result.driver_standing_position(driver)
            if position is not None and position <= 3:
                return True

        return False

    #
    # Diagram queries
    #

    def cumulative_points_data(self) -> str:
        data: Dict[Any, Any] = dict()

        data["labels"] = [0] + [
            race.name for race in sorted(self.all_races(), key=lambda race: race.number)
        ]

        data["datasets"] = [
            {
                "data": self.points_per_step_cumulative()[user.name],
                "label": user.name,
                "fill": False,
            }
            for user in self.all_users()
        ]

        return json.dumps(data)

    def cumulative_driver_points_data(self) -> str:
        data: Dict[Any, Any] = dict()

        data["labels"] = [0] + [
            race.name for race in sorted(self.all_races(), key=lambda race: race.number)
        ]

        data["datasets"] = [
            {
                "data": self.driver_points_per_step_cumulative()[driver.name],
                "label": driver.abbr,
                "fill": False,
            }
            for driver in self.all_drivers(include_none=False, include_inactive=True)
        ]

        return json.dumps(data)

    def cumulative_team_points_data(self) -> str:
        data: Dict[Any, Any] = dict()

        data["labels"] = [0] + [
            race.name for race in sorted(self.all_races(), key=lambda race: race.number)
        ]

        data["datasets"] = [
            {
                "data": self.team_points_per_step_cumulative()[team.name],
                "label": team.name,
                "fill": False,
            }
            for team in self.all_teams(include_none=False)
        ]

        return json.dumps(data)
