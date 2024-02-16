from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import json

db = SQLAlchemy()

####################################
# Static Data (Defined in Backend) #
####################################


class Race(db.Model):
    __tablename__ = "race"

    def from_csv(self, row):
        self.id = int(row[0])
        self.grandprix = str(row[1])
        self.number = int(row[2])
        self.date = datetime.strptime(row[3], "%Y-%m-%d")
        self.pxx = int(row[4])  # This is the place that has to be guessed for this race
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grandprix: Mapped[str] = mapped_column(String(32))
    number: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime)
    pxx: Mapped[int] = mapped_column(Integer)


class Team(db.Model):
    __tablename__ = "team"

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class Driver(db.Model):
    __tablename__ = "driver"

    def from_csv(self, row):
        self.name = str(row[0])
        self.abbr = str(row[1])
        self.team_id = str(row[2])
        self.country_code = str(row[3])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    abbr: Mapped[str] = mapped_column(String(3))
    team_id: Mapped[str] = mapped_column(ForeignKey("team.name"))
    country_code: Mapped[str] = mapped_column(String(2))  # alpha-2 code

    # Relationships
    team: Mapped["Team"] = relationship("Team", foreign_keys=[team_id])


######################################
# Dynamic Data (Defined in Frontend) #
######################################


class User(db.Model):
    __tablename__ = "user"
    __csv_header__ = ["name"]

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    def to_csv(self):
        return [
            self.name
        ]

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class RaceResult(db.Model):
    __tablename__ = "raceresult"
    __csv_header__ = ["id", "race_id", "pxx_ids_json", "dnf_ids_json"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.race_id = int(row[1])
        self.pxx_ids_json = str(row[2])
        self.dnf_ids_json = str(row[3])
        return self

    def to_csv(self):
        return [
            self.id,
            self.race_id,
            self.pxx_ids_json,
            self.dnf_ids_json
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("race.id"))
    pxx_ids_json: Mapped[str] = mapped_column(String(1024))
    dnf_ids_json: Mapped[str] = mapped_column(String(1024))

    @property
    def pxx_ids(self) -> List[str]:
        return json.loads(self.pxx_ids_json)

    @pxx_ids.setter
    def pxx_ids(self, new_pxx_ids: List[str]):
        self.pxx_ids_json = json.dumps(new_pxx_ids)

    @property
    def dnf_ids(self) -> List[str]:
        return json.loads(self.dnf_ids_json)

    @dnf_ids.setter
    def dnf_ids(self, new_dnf_ids: List[str]):
        self.dnf_ids_json = json.dumps(new_dnf_ids)

    # Relationships
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    _pxxs = None
    _dnfs = None

    @property
    def pxxs(self) -> List[Driver]:
        if self._pxxs is None:
            self._pxxs = [
                driver for driver in Driver.query.all() if driver.name in self.pxx_ids
            ]

        return self._pxxs

    @property
    def dnfs(self) -> List[Driver]:
        if self._dnfs is None:
            self._dnfs = [
                driver for driver in Driver.query.all() if driver.name in self.dnf_ids
            ]

        return self._dnfs


class RaceGuess(db.Model):
    __tablename__ = "raceguess"
    __csv_header__ = ["id", "user_id", "race_id", "pxx_id", "dnf_id"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.race_id = int(row[2])
        self.pxx_id = str(row[3])
        self.dnf_id = str(row[4])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.race_id,
            self.pxx_id,
            self.dnf_id
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    race_id: Mapped[int] = mapped_column(ForeignKey("race.id"))
    pxx_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    pxx: Mapped["Driver"] = relationship("Driver", foreign_keys=[pxx_id])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])


class TeamWinners(db.Model):
    __tablename__ = "teamwinners"
    __csv_header__ = ["id", "user_id", "winner_ids_json"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.winner_ids_json = str(row[2])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.winner_ids_json
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    winner_ids_json: Mapped[str] = mapped_column(String(512))

    @property
    def winner_ids(self) -> List[str]:
        return json.loads(self.winner_ids_json)

    @winner_ids.setter
    def winner_ids(self, new_winner_ids: List[str]):
        self.winner_ids_json = json.dumps(new_winner_ids)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    _winners = None

    @property
    def winners(self) -> List[Driver]:
        if self._winners is None:
            self._winners = [
                driver for driver in Driver.query.all() if driver.name in self.winner_ids
            ]

        return self._winners


class PodiumDrivers(db.Model):
    __tablename__ = "podiumdrivers"
    __csv_header__ = ["id", "user_id", "podium_ids_json"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.podium_ids_json = str(row[2])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.podium_ids_json
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    podium_ids_json: Mapped[str] = mapped_column(String(512))

    @property
    def podium_ids(self) -> List[str]:
        return json.loads(self.podium_ids_json)

    @podium_ids.setter
    def podium_ids(self, new_podium_ids: List[str]):
        self.podium_ids_json = json.dumps(new_podium_ids)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    _podiums = None

    @property
    def podiums(self) -> List[Driver]:
        if self._podiums is None:
            self._podiums = [
                driver for driver in Driver.query.all() if driver.name in self.podium_ids
            ]

        return self._podiums


class SeasonGuess(db.Model):
    __tablename__ = "seasonguess"
    __csv_header__ = ["id", "user_id",
                      "hot_take", "p2_constructor_id", "most_overtakes_id", "most_dnfs_id", "most_gained_id",
                      "most_lost_id", "team_winners_id", "podium_drivers_id"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.hot_take = str(row[2])
        self.p2_constructor_id = str(row[3])
        self.most_overtakes_id = str(row[4])
        self.most_dnfs_id = str(row[5])
        self.most_gained_id = str(row[6])
        self.most_lost_id = str(row[6])
        self.team_winners_id = int(row[8])
        self.podium_drivers_id = int(row[9])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.hot_take,
            self.p2_constructor_id,
            self.most_overtakes_id,
            self.most_dnfs_id,
            self.most_gained_id,
            self.most_lost_id,
            self.team_winners_id,
            self.podium_drivers_id
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    hot_take: Mapped[str] = mapped_column(String(512))
    p2_constructor_id: Mapped[str] = mapped_column(ForeignKey("team.name"))
    most_overtakes_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    most_dnfs_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    most_gained_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    most_lost_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    team_winners_id: Mapped[int] = mapped_column(ForeignKey("teamwinners.id"))
    podium_drivers_id: Mapped[int] = mapped_column(ForeignKey("podiumdrivers.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    p2_constructor: Mapped["Team"] = relationship("Team", foreign_keys=[p2_constructor_id])
    most_overtakes: Mapped["Driver"] = relationship("Driver", foreign_keys=[most_overtakes_id])
    most_dnfs: Mapped["Driver"] = relationship("Driver", foreign_keys=[most_dnfs_id])
    most_gained: Mapped["Driver"] = relationship("Driver", foreign_keys=[most_gained_id])
    most_lost: Mapped["Driver"] = relationship("Driver", foreign_keys=[most_lost_id])
    team_winners: Mapped["TeamWinners"] = relationship("TeamWinners", foreign_keys=[team_winners_id])
    podium_drivers: Mapped["PodiumDrivers"] = relationship("PodiumDrivers", foreign_keys=[podium_drivers_id])
