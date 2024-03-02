from typing import Dict, List, overload
import numpy as np

from formula10.domain.domain_model import Model
from formula10.domain.model.driver import NONE_DRIVER
from formula10.domain.model.race_guess import RaceGuess
from formula10.domain.model.race_result import RaceResult

RACE_GUESS_OFFSET_POINTS: Dict[int, int] = {
    3: 1,
    2: 3,
    1: 6,
    0: 10
}
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

STANDING_2023: Dict[str, int] = {
    "Max Verstappen": 1,
    "Sergio Perez": 2,
    "Lewis Hamilton": 3,
    "Fernando Alonso": 4,
    "Charles Leclerc": 5,
    "Lando Norris": 6,
    "Carlos Sainz": 7,
    "George Russel": 8,
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
    "Logan Sargeant": 21
}

def standing_points(race_guess: RaceGuess, race_result: RaceResult) -> int:
    guessed_driver_position: int | None = race_result.driver_standing_position(driver=race_guess.pxx_guess)
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

class PointsModel(Model):
    """
    This class bundles all data + functionality required to do points calculations.
    """

    _points_per_step: Dict[str, List[int]] | None = None

    def __init__(self):
        Model.__init__(self)

    def points_per_step(self) -> Dict[str, List[int]]:
        """
        Returns a dictionary of lists, containing points per race for each user.
        """
        if self._points_per_step is None:
            self._points_per_step = dict()
            for user in self.all_users():
                self._points_per_step[user.name] = [0] * 24  # Start at index 1, like the race numbers

            for race_guess in self.all_race_guesses():
                user_name: str = race_guess.user.name
                race_number: int = race_guess.race.number
                race_result: RaceResult | None = self.race_result_by(race_name=race_guess.race.name)

                if race_result is None:
                    continue

                self._points_per_step[user_name][race_number] = standing_points(race_guess, race_result) + dnf_points(race_guess, race_result)

        return self._points_per_step

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

    def points_by(self, *, user_name: str | None = None, race_name: str | None = None) -> List[int] | Dict[str, int] | int:
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

    def total_points_by(self, user_name: str) -> int:
        """
        Returns the total number of points for a specific user.
        """
        return sum(self.points_by(user_name=user_name))

    def picks_count(self, user_name: str) -> int:
        # Treat standing + dnf picks separately
        return len(self.race_guesses_by(user_name=user_name)) * 2

    def picks_with_points_count(self, user_name: str) -> int:
        count: int = 0

        for race_guess in self.race_guesses_by(user_name=user_name):
            race_result: RaceResult | None = self.race_result_by(race_name=race_guess.race.name)
            if race_result is None:
                continue

            if standing_points(race_guess, race_result) > 0:
                count = count + 1
            if dnf_points(race_guess, race_result) > 0:
                count = count + 1

        return count

    def points_per_pick(self, user_name: str) -> float:
        if self.picks_count(user_name) == 0:
            return 0.0

        return self.total_points_by(user_name) / self.picks_count(user_name)
