import json
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

####################################
# Static Data (Defined in Backend) #
####################################


class Race(db.Model):
    """
    A single race at a certain date and GrandPrix in the calendar.
    It stores the place to guess for this race.
    """
    __tablename__ = "race"

    def from_csv(self, row):
        self.name = str(row[0])
        self.number = int(row[1])
        self.date = datetime.strptime(row[2], "%Y-%m-%d")
        self.pxx = int(row[3])
        return self

    @property
    def name_sanitized(self):
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

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class Driver(db.Model):
    """
    A F1 driver.
    It stores the corresponding team + name abbreviation.
    """
    __tablename__ = "driver"

    def from_csv(self, row):
        self.name = str(row[0])
        self.abbr = str(row[1])
        self.team_name = str(row[2])
        self.country_code = str(row[3])
        return self

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

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    def to_csv(self):
        return [
            self.name
        ]

    @property
    def name_sanitized(self):
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

    def from_csv(self, row):
        self.race_name = str(row[0])
        self.pxx_driver_names_json = str(row[1])
        self.dnf_driver_names_json = str(row[2])
        self.excluded_driver_names_json = str(row[3])
        return self

    def to_csv(self):
        return [
            self.race_name,
            self.pxx_driver_names_json,
            self.dnf_driver_names_json,
            self.excluded_driver_names_json
        ]

    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_names_json: Mapped[str] = mapped_column(String(1024))
    dnf_driver_names_json: Mapped[str] = mapped_column(String(1024))
    excluded_driver_names_json: Mapped[str] = mapped_column(String(1024))

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
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._pxx_drivers[position] = driver

        return self._pxx_drivers

    @property
    def pxx_drivers_values(self) -> List[Driver]:
        drivers: List[Driver] = []

        # I don't know what order dict.values() etc. will return...
        for position in range(1, 21):
            drivers += [self.pxx_drivers[str(position)]]

        return drivers

    @property
    def dnf_drivers(self) -> Dict[str, Driver]:
        if self._dnf_drivers is None:
            self._dnf_drivers = dict()
            for position, driver_name in self.dnf_driver_names.items():
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._dnf_drivers[position] = driver

        return self._dnf_drivers

    @property
    def excluded_drivers(self) -> List[Driver]:
        if self._excluded_drivers is None:
            self._excluded_drivers = []
            for driver_name in self.excluded_driver_names:
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._excluded_drivers += [driver]

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

    def from_csv(self, row):
        self.user_name = str(row[0])
        self.race_name = str(row[1])
        self.pxx_driver_name = str(row[2])
        self.dnf_driver_name = str(row[3])
        return self

    def to_csv(self):
        return [
            self.user_name,
            self.race_name,
            self.pxx_driver_name,
            self.dnf_driver_name
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    race_name: Mapped[str] = mapped_column(ForeignKey("race.name"), primary_key=True)
    pxx_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))

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

    def from_csv(self, row):
        self.user_name = str(row[0])
        self.teamwinner_driver_names_json = str(row[1])
        return self

    def to_csv(self):
        return [
            self.user_name,
            self.teamwinner_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    teamwinner_driver_names_json: Mapped[str] = mapped_column(String(1024))

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
            self._teamwinner_drivers = []
            for driver_name in self.teamwinner_driver_names:
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._teamwinner_drivers += [driver]

        return self._teamwinner_drivers


class PodiumDrivers(db.Model):
    """
    A guessed list of each driver that will reach at least a single podium.
    """
    __tablename__ = "podiumdrivers"
    __allow_unmapped__ = True
    __csv_header__ = ["user_name", "podium_driver_names_json"]

    def from_csv(self, row):
        self.user_name = str(row[0])
        self.podium_driver_names_json = str(row[1])
        return self

    def to_csv(self):
        return [
            self.user_name,
            self.podium_driver_names_json
        ]

    user_name: Mapped[str] = mapped_column(ForeignKey("user.name"), primary_key=True)
    podium_driver_names_json: Mapped[str] = mapped_column(String(1024))

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
            self._podium_drivers = []
            for driver_name in self.podium_driver_names:
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver is None:
                    raise Exception(f"Error: Couldn't find driver with id {driver_name}")

                self._podium_drivers += [driver]

        return self._podium_drivers


class SeasonGuess(db.Model):
    """
    A collection of bonus guesses for the entire season.
    """
    __tablename__ = "seasonguess"
    __csv_header__ = ["user_name", "hot_take", "p2_team_name",
                      "overtake_driver_name", "dnf_driver_name", "gained_driver_name", "lost_driver_name",
                      "team_winners_id", "podium_drivers_id"]

    def from_csv(self, row):
        self.user_name = str(row[0])  # Also used as foreign key for teamwinners + podiumdrivers
        self.hot_take = str(row[1])
        self.p2_team_name = str(row[2])
        self.overtake_driver_name = str(row[3])
        self.dnf_driver_name = str(row[4])
        self.gained_driver_name = str(row[5])
        self.lost_driver_name = str(row[6])
        self.team_winners_id = str(row[7])
        self.podium_drivers_id = str(row[8])
        return self

    def to_csv(self):
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
    hot_take: Mapped[str] = mapped_column(String(512))
    p2_team_name: Mapped[str] = mapped_column(ForeignKey("team.name"))
    overtake_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    gained_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    lost_driver_name: Mapped[str] = mapped_column(ForeignKey("driver.name"))

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
