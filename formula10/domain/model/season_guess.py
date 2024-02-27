import json
from typing import List
from formula10.database.common_queries import find_single_driver_strict
from formula10.database.model.db_season_guess import DbSeasonGuess
from formula10.domain.model.driver import Driver
from formula10.domain.model.team import Team
from formula10.domain.model.user import User


class SeasonGuess():
    @classmethod
    def from_db_season_guess(cls, db_season_guess: DbSeasonGuess):
        season_guess: SeasonGuess = cls()
        season_guess.user = User.from_db_user(db_season_guess.user)
        season_guess.hot_take = db_season_guess.hot_take if db_season_guess.hot_take is not None else None
        season_guess.p2_wcc = Team.from_db_team(db_season_guess.p2_team) if db_season_guess.p2_team is not None else None
        season_guess.most_overtakes = Driver.from_db_driver(db_season_guess.overtake_driver) if db_season_guess.overtake_driver is not None else None
        season_guess.most_dnfs = Driver.from_db_driver(db_season_guess.dnf_driver) if db_season_guess.dnf_driver is not None else None
        season_guess.most_wdc_gained = Driver.from_db_driver(db_season_guess.gained_driver) if db_season_guess.gained_driver is not None else None
        season_guess.most_wdc_lost = Driver.from_db_driver(db_season_guess.lost_driver) if db_season_guess.lost_driver is not None else None

        # Deserialize from json
        team_winners: List[str | None] = json.loads(db_season_guess.team_winners_driver_names_json)
        podiums: List[str] = json.loads(db_season_guess.podium_drivers_driver_names_json)

        # Populate relationships
        season_guess.team_winners = [
            Driver.from_db_driver(find_single_driver_strict(driver_name)) if driver_name is not None else None
            for driver_name in team_winners
        ]
        season_guess.podiums = [
            Driver.from_db_driver(find_single_driver_strict(driver_name))
            for driver_name in podiums
        ]

        return season_guess

    def to_db_season_guess(self):
        # "Unpopulate" relationships
        team_winners: List[str | None] = [
            driver.name if driver is not None else None
            for driver in self.team_winners
        ]
        podiums: List[str] = [
            driver.name for driver in self.podiums
        ]

        # Serialize to json
        db_season_guess: DbSeasonGuess = DbSeasonGuess(user_name=self.user.name,
                                                       team_winners_driver_names_json=json.dumps(team_winners),
                                                       podium_drivers_driver_names_json=json.dumps(podiums))
        db_season_guess.user_name = self.user.name
        db_season_guess.hot_take = self.hot_take
        db_season_guess.p2_team_name = self.p2_wcc.name if self.p2_wcc is not None else None
        db_season_guess.overtake_driver_name = self.most_overtakes.name if self.most_overtakes is not None else None
        db_season_guess.dnf_driver_name = self.most_dnfs.name if self.most_dnfs is not None else None
        db_season_guess.gained_driver_name = self.most_wdc_gained.name if self.most_wdc_gained is not None else None
        db_season_guess.lost_driver_name = self.most_wdc_lost.name if self.most_wdc_lost is not None else None

        return db_season_guess

    user: User
    hot_take: str | None
    p2_wcc: Team | None
    most_overtakes: Driver | None
    most_dnfs: Driver | None
    most_wdc_gained: Driver | None
    most_wdc_lost: Driver | None
    team_winners: List[Driver | None]
    podiums: List[Driver]

    def hot_take_string(self) -> str:
        return self.hot_take if self.hot_take is not None else ""
