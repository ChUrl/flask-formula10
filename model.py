import json
from datetime import datetime
from typing import Any, List, Dict
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db: SQLAlchemy = SQLAlchemy()

####################################
# Static Data (Defined in Backend) #
####################################


class Race(db.Model):
    """
    A single race at a certain date and GrandPrix in the calendar.
    It stores the place to guess for this race.
    """
    __tablename__ = "race"

    @staticmethod
    def from_csv(row: List[str]):
        race: Race = Race()
        race.name = str(row[0])
        race.number = int(row[1])
        race.date = datetime.strptime(row[2], "%Y-%m-%d")
        race.pxx = int(row[3])
        return race

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    number: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime)
    pxx: Mapped[int] = mapped_column(Integer)  # This is the place to guess


class Team(db.Model):
    """
    A constructor/team (name only).
    """
    __tablename__ = "team"

    @staticmethod
    def from_csv(row: List[str]):
        team: Team = Team()
        team.name = str(row[0])
        return team

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class Driver(db.Model):
    """
    A F1 driver.
    It stores the corresponding team + name abbreviation.
    """
    __tablename__ = "driver"

    @staticmethod
    def from_csv(row: List[str]):
        driver: Driver = Driver()
        driver.name = str(row[0])
        driver.abbr = str(row[1])
        driver.team_name = str(row[2])
        driver.country_code = str(row[3])
        return driver

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    abbr: Mapped[str] = mapped_column(String(3))
    team_name: Mapped[str] = mapped_column(ForeignKey("team.name"))
    country_code: Mapped[str] = mapped_column(String(2))  # alpha-2 code

    # Relationships
    team: Mapped["Team"] = relationship("Team", foreign_keys=[team_name])


######################################
# Dynamic Data (Defined in Frontend) #
######################################


class User(db.Model):
    """
    A user that can guess races (name only).
    """
    __tablename__ = "user"
    __csv_header__ = ["name"]

    def __init__(self, name: str):
        self.name = name  # Primary key

    @staticmethod
    def from_csv(row: List[str]):
        user: User = User(str(row[0]))
        return user

    def to_csv(self) -> List[Any]:
        return [
            self.name
        ]

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class RaceResult(db.Model):
    """
    The result of a past race.
    It stores the corresponding race and dictionaries of place-/dnf-order and a list of drivers that are excluded from the standings for this race.
    """
    __tablename__ = "raceresult"
    __allow_unmapped__ = True  # TODO: Used for json conversion, move this to some other class instead
    __csv_header__ = ["race_name", "pxx_driver_names_json", "dnf_driver_names_json", "excluded_driver_names_json"]

    def __init__(self, race_name: str):
        self.race_name = race_name  # Primary key

    @staticmethod
    def from_csv(row: List[str]):
        race_result: RaceResult = RaceResult(str(row[0]))
        race_result.pxx_driver_names_json = str(row[1])
        race_result.dnf_driver_names_json = str(row[2])
        race_result.excluded_driver_names_json = str(row[3])
        return race_result

    def to_csv(self) -> List[Any]:
        return [
            self.race_name,
            self.pxx_driver_names_json,
            self.dnf_driver_names_json,
            self.excluded_driver_names_json
        ]

    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)
    dnf_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)
    excluded_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)

    @property
    def pxx_driver_names(self) -> Dict[str, str]:
        return json.loads(self.pxx_driver_names_json)

    @pxx_driver_names.setter
    def pxx_driver_names(self, new_pxx_driver_names: Dict[str, str]):
        self.pxx_driver_names_json = json.dumps(new_pxx_driver_names)

    @property
    def dnf_driver_names(self) -> Dict[str, str]:
        return json.loads(self.dnf_driver_names_json)

    @dnf_driver_names.setter
    def dnf_driver_names(self, new_dnf_driver_names: Dict[str, str]):
        self.dnf_driver_names_json = json.dumps(new_dnf_driver_names)

    @property
    def excluded_driver_names(self) -> List[str]:
        return json.loads(self.excluded_driver_names_json)

    @excluded_driver_names.setter
    def excluded_driver_names(self, new_excluded_driver_names: List[str]):
        self.excluded_driver_names_json = json.dumps(new_excluded_driver_names)

    # Relationships
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_name])
    _pxx_drivers: Dict[str, Driver] | None = None
    _dnf_drivers: Dict[str, Driver] | None = None
    _excluded_drivers: List[Driver] | None = None

    @property
    def pxx_drivers(self) -> Dict[str, Driver]:
        if self._pxx_drivers is None:
            self._pxx_drivers = dict()
            for position, driver_name in self.pxx_driver_names.items():
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._pxx_drivers[position] = driver

        return self._pxx_drivers

    @property
    def pxx_drivers_values(self) -> List[Driver]:
        drivers: List[Driver] = list()

        # I don't know what order dict.values() etc. will return...
        for position in range(1, 21):
            drivers.append(self.pxx_drivers[str(position)])

        return drivers

    @property
    def dnf_drivers(self) -> Dict[str, Driver]:
        if self._dnf_drivers is None:
            self._dnf_drivers = dict()
            for position, driver_name in self.dnf_driver_names.items():
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._dnf_drivers[position] = driver

        return self._dnf_drivers

    @property
    def excluded_drivers(self) -> List[Driver]:
        if self._excluded_drivers is None:
            self._excluded_drivers = list()
            for driver_name in self.excluded_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._excluded_drivers.append(driver)

        return self._excluded_drivers

    def pxx(self, offset: int = 0) -> Driver:
        pxx_num: str = str(self.race.pxx + offset)
        if pxx_num not in self.pxx_drivers:
            raise Exception(f"Error: Position {self.race.pxx} not contained in race result")

        return self.pxx_drivers[pxx_num]

    @property
    def dnf(self) -> Driver:
        return sorted(self.dnf_drivers.items(), reverse=True)[0][1]  # SortedList[FirstElement][KeyPairValue]


class RaceGuess(db.Model):
    """
    A guess a user made for a race.
    It stores the corresponding race and the guessed drivers for PXX and DNF.
    """
    __tablename__ = "raceguess"
    __csv_header__ = ["user_name", "race_name", "pxx_driver_name", "dnf_driver_name"]

    def __init__(self, user_name: str, race_name: str):
        self.user_name = user_name  # Primary key
        self.race_name = race_name  # Primery key

    @staticmethod
    def from_csv(row: List[str]):
        race_guess: RaceGuess = RaceGuess(str(row[0]), str(row[1]))
        race_guess.pxx_driver_name = str(row[2])
        race_guess.dnf_driver_name = str(row[3])
        return race_guess

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.race_name,
            self.pxx_driver_name,
            self.dnf_driver_name
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_name])
    pxx: Mapped["Driver"] = relationship("Driver", foreign_keys=[pxx_driver_name])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_driver_name])


class TeamWinners(db.Model):
    """
    A guessed list of each best driver per team.
    """
    __tablename__ = "teamwinners"
    __allow_unmapped__ = True
    __csv_header__ = ["user_name", "teamwinner_driver_names_json"]

    def __init__(self, user_name: str):
        self.user_name = user_name  # Primary key

    @staticmethod
    def from_csv(row: List[str]):
        team_winners: TeamWinners = TeamWinners(str(row[0]))
        team_winners.teamwinner_driver_names_json = str(row[1])
        return team_winners

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.teamwinner_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    teamwinner_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)

    @property
    def teamwinner_driver_names(self) -> List[str]:
        return json.loads(self.teamwinner_driver_names_json)

    @teamwinner_driver_names.setter
    def teamwinner_driver_names(self, new_teamwinner_driver_names: List[str]):
        self.teamwinner_driver_names_json = json.dumps(new_teamwinner_driver_names)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    _teamwinner_drivers: List[Driver] | None = None

    @property
    def teamwinners(self) -> List[Driver]:
        if self._teamwinner_drivers is None:
            self._teamwinner_drivers = list()
            for driver_name in self.teamwinner_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._teamwinner_drivers.append(driver)

        return self._teamwinner_drivers


class PodiumDrivers(db.Model):
    """
    A guessed list of each driver that will reach at least a single podium.
    """
    __tablename__ = "podiumdrivers"
    __allow_unmapped__ = True
    __csv_header__ = ["user_name", "podium_driver_names_json"]

    def __init__(self, user_name: str):
        self.user_name = user_name

    @staticmethod
    def from_csv(row: List[str]):
        podium_drivers: PodiumDrivers = PodiumDrivers(str(row[0]))
        podium_drivers.podium_driver_names_json = str(row[1])
        return podium_drivers

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.podium_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    podium_driver_names_json: Mapped[str] = mapped_column(String(1024), nullable=True)

    @property
    def podium_driver_names(self) -> List[str]:
        return json.loads(self.podium_driver_names_json)

    @podium_driver_names.setter
    def podium_driver_names(self, new_podium_driver_names: List[str]):
        self.podium_driver_names_json = json.dumps(new_podium_driver_names)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    _podium_drivers: List[Driver] | None = None

    @property
    def podium_drivers(self) -> List[Driver]:
        if self._podium_drivers is None:
            self._podium_drivers = list()
            for driver_name in self.podium_driver_names:
                driver: Driver | None = db.session.query(Driver).filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._podium_drivers.append(driver)

        return self._podium_drivers


class SeasonGuess(db.Model):
    """
    A collection of bonus guesses for the entire season.
    """
    __tablename__ = "seasonguess"
    __csv_header__ = ["user_name", "hot_take", "p2_team_name",
                      "overtake_driver_name", "dnf_driver_name", "gained_driver_name", "lost_driver_name",
                      "team_winners_id", "podium_drivers_id"]

    def __init__(self, user_name: str, team_winners_user_name: str | None = None, podium_drivers_user_name: str | None = None):
        self.user_name = user_name  # Primary key

        # Although this is the same username, handle separately, in case they don't exist in the database yet
        if team_winners_user_name is not None:
            if user_name != team_winners_user_name:
                raise Exception(f"SeasonGuess for {user_name} was supplied TeamWinners for {team_winners_user_name}")

            self.team_winners_id = team_winners_user_name

        if podium_drivers_user_name is not None:
            if user_name != podium_drivers_user_name:
                raise Exception(f"SeasonGuess for {user_name} was supplied PodiumDrivers for {podium_drivers_user_name}")

            self.podium_drivers_id = podium_drivers_user_name

    @staticmethod
    def from_csv(row: List[str]):
        season_guess: SeasonGuess = SeasonGuess(str(row[0]), team_winners_user_name=str(row[7]), podium_drivers_user_name=str(row[8]))
        season_guess.hot_take = str(row[1])
        season_guess.p2_team_name = str(row[2])
        season_guess.overtake_driver_name = str(row[3])
        season_guess.dnf_driver_name = str(row[4])
        season_guess.gained_driver_name = str(row[5])
        season_guess.lost_driver_name = str(row[6])
        return season_guess

    def to_csv(self) -> List[Any]:
        return [
            self.user_name,
            self.hot_take,
            self.p2_team_name,
            self.overtake_driver_name,
            self.dnf_driver_name,
            self.gained_driver_name,
            self.lost_driver_name,
            self.team_winners_id,
            self.podium_drivers_id
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    hot_take: Mapped[str] = mapped_column(String(512), nullable=True)
    p2_team_name: Mapped[str] = mapped_column(ForeignKey("team.name"), nullable=True)
    overtake_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    gained_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)
    lost_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"), nullable=True)

    team_winners_id: Mapped[str] = mapped_column(ForeignKey("teamwinners.user_name"))
    podium_drivers_id: Mapped[str] = mapped_column(ForeignKey("podiumdrivers.user_name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_name])
    p2_team: Mapped["Team"] = relationship("Team", foreign_keys=[p2_team_name])
    overtake_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[overtake_driver_name])
    dnf_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_driver_name])
    gained_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[gained_driver_name])
    lost_driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[lost_driver_name])

    team_winners: Mapped["TeamWinners"] = relationship("TeamWinners", foreign_keys=[team_winners_id])
    podium_drivers: Mapped["PodiumDrivers"] = relationship("PodiumDrivers", foreign_keys=[podium_drivers_id])
