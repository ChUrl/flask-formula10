import json
from typing import Dict, List

from formula10.database.common_queries import find_single_driver_strict
from formula10.database.model.db_race_result import DbRaceResult
from formula10.domain.model.driver import NONE_DRIVER, Driver
from formula10.domain.model.race import Race


class RaceResult:
    @classmethod
    def from_db_race_result(cls, db_race_result: DbRaceResult):
        race_result: RaceResult = cls()
        race_result.race = Race.from_db_race(db_race_result.race)
        race_result.fastest_lap_driver = Driver.from_db_driver(db_race_result.fastest_lap_driver)

        # Deserialize from json
        standing: Dict[str, str] = json.loads(db_race_result.pxx_driver_ids_json)
        initial_dnf: List[str] = json.loads(db_race_result.first_dnf_driver_ids_json)
        all_dnfs: List[str] = json.loads(db_race_result.dnf_driver_ids_json)
        standing_exclusions: List[str] = json.loads(db_race_result.excluded_driver_ids_json)
        sprint_dnfs: List[str] = json.loads(db_race_result.sprint_dnf_driver_ids_json)
        sprint_standing: Dict[str, str] = json.loads(db_race_result.sprint_points_json)

        # Populate relationships
        race_result.standing = {
            position: Driver.from_db_driver(find_single_driver_strict(int(driver_id)))
            for position, driver_id in standing.items()
        }
        race_result.initial_dnf = [
            Driver.from_db_driver(find_single_driver_strict(int(driver_id)))
            for driver_id in initial_dnf
        ]
        race_result.all_dnfs = [
            Driver.from_db_driver(find_single_driver_strict(int(driver_id)))
            for driver_id in all_dnfs
        ]
        race_result.standing_exclusions = [
            Driver.from_db_driver(find_single_driver_strict(int(driver_id)))
            for driver_id in standing_exclusions
        ]
        race_result.sprint_dnfs = [
            Driver.from_db_driver(find_single_driver_strict(int(driver_id)))
            for driver_id in sprint_dnfs
        ]
        race_result.sprint_standing = {
            position: Driver.from_db_driver(find_single_driver_strict(int(driver_id)))
            for position, driver_id in sprint_standing.items()
        }

        return race_result

    def to_db_race_result(self) -> DbRaceResult:
        # "Unpopulate" relationships, remove none driver
        standing: Dict[str, str] = {
            position: driver.name for position, driver in self.standing.items()
        }
        initial_dnf: List[str] = [
            str(driver.id) for driver in self.initial_dnf if driver
        ]
        all_dnfs: List[str] = [
            str(driver.id) for driver in self.all_dnfs if driver
        ]
        standing_exclusions: List[str] = [
            str(driver.id) for driver in self.standing_exclusions if driver
        ]
        sprint_dnfs: List[str] = [
            str(driver.id) for driver in self.sprint_dnfs if driver
        ]
        sprint_standing: Dict[str, str] = {
            position: driver.name for position, driver in self.sprint_standing.items()
        }

        # Serialize to json
        db_race_result: DbRaceResult = DbRaceResult(race_id=self.race.id)
        db_race_result.pxx_driver_ids_json = json.dumps(standing)
        db_race_result.first_dnf_driver_ids_json = json.dumps(initial_dnf)
        db_race_result.dnf_driver_ids_json = json.dumps(all_dnfs)
        db_race_result.excluded_driver_ids_json = json.dumps(standing_exclusions)
        db_race_result.fastest_lap_id = self.fastest_lap_driver.id
        db_race_result.sprint_dnf_driver_ids_json = json.dumps(sprint_dnfs)
        db_race_result.sprint_points_json = json.dumps(sprint_standing)

        return db_race_result

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, RaceResult):
            return self.race == __value.race

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.race)

    race: Race
    standing: Dict[str, Driver]  # Always contains all 20 drivers, even if DNF'ed or excluded
    initial_dnf: List[Driver]  # initial_dnf is empty if no-one DNF'ed
    all_dnfs: List[Driver]
    standing_exclusions: List[Driver]

    fastest_lap_driver: Driver
    sprint_dnfs: List[Driver]
    sprint_standing: Dict[str, Driver]

    def offset_from_place_to_guess(self, offset: int, respect_nc:bool = True) -> Driver:
        position: str = str(self.race.place_to_guess + offset)

        if position not in self.standing:
            raise Exception(f"Position {position} not found in RaceResult.standing")

        if self.standing[position] in self.standing_exclusions and respect_nc:
            return NONE_DRIVER

        return self.standing[position]

    def driver_standing_position(self, driver: Driver) -> int | None:
        if driver == NONE_DRIVER:
            return None

        for position, _driver in self.standing.items():
            if driver == _driver and driver not in self.standing_exclusions:
                return int(position)

        return None

    def driver_standing_position_string(self, driver: Driver) -> str:
        if driver == NONE_DRIVER:
            return ""

        for position, _driver in self.standing.items():
            if driver == _driver and driver not in self.standing_exclusions:
                return f" (P{position})"

        return " (NC)"

    def driver_standing_points_string(self, driver: Driver) -> str:
        points_strings: Dict[int, str] = {
            0: "10 Points",
            1: "6 Points",
            2: "3 Points",
            3: "1 Points"
        }

        if driver == NONE_DRIVER:
            if self.standing[str(self.race.place_to_guess)] in self.standing_exclusions:
                return "10 Points"
            else:
                return "0 Points"

        for position, _driver in self.standing.items():
            if driver == _driver and driver not in self.standing_exclusions:
                position_offset: int = abs(self.race.place_to_guess - int(position))
                if position_offset in points_strings:
                    return points_strings[position_offset]
                else:
                    return "0 Points"

        raise Exception(f"Could not get points string for driver {driver.name}")

    def driver_dnf_points_string(self, driver: Driver) -> str:
        if driver == NONE_DRIVER:
            if len(self.initial_dnf) == 0:
                return "10 Points"
            else:
                return "0 Points"

        if driver in self.initial_dnf:
            return "10 Points"
        else:
            return "0 Points"

    def ordered_standing_list(self) -> List[Driver]:
        return [
            self.standing[str(position)] for position in range(1, 21)
        ]

    def ordered_sprint_standing_list(self) -> List[Driver]:
        return [
            self.sprint_standing[str(position)] for position in range(1, 21)
        ]

    def initial_dnf_string(self) -> str:
        if len(self.initial_dnf) == 0:
            return NONE_DRIVER.name

        dnf_string: str = ""
        for driver in self.initial_dnf:
            dnf_string += f"{driver.abbr} "

        return dnf_string[0:len(dnf_string)-1] # Remove last space
