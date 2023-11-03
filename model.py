from copyreg import constructor
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, Date, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime as dt
import re

db = SQLAlchemy()

# Modeling these entities separately should make it easier to add new guess categories, for example team guesses or GP guesses

def optional_date(date_string):
    if date_string == "\\N":
        return None

    return dt.date.fromisoformat(date_string)

def optional_time(time_string):
    if time_string == "\\N":
        return None

    pattern = re.compile(r"^.?:.?.?\..*$")
    if pattern.match(time_string):
        time_string = "0" + time_string

    return dt.time.fromisoformat(time_string)

def optional_int(int_string):
    if int_string == "\\N":
        return None

    return int(int_string)

def optional_str(str_string):
    if str_string == "\\N":
        return None

    return str(str_string)

class Circuit(db.Model):
    __tablename__ = "circuit"

    def from_csv(self, row):
        self.circuitId = int(row[0])
        self.circuitRef = str(row[1])
        self.name = str(row[2])
        self.location = str(row[3])
        self.country = str(row[4])
        return self

    circuitId: Mapped[int] = mapped_column(Integer, primary_key=True)
    circuitRef: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(128))
    location: Mapped[str] = mapped_column(String(128))
    country: Mapped[str] = mapped_column(String(128))

class Season(db.Model):
    __tablename__ = "season"

    def from_csv(self, row):
        self.year = int(row[0])
        return self

    year: Mapped[int] = mapped_column(Integer, primary_key=True) # This is the year

class Race(db.Model):
    __tablename__ = "race"

    def from_csv(self, row):
        self.raceId = int(row[0])
        self.year = int(row[1])
        self.round = int(row[2])
        self.circuitId = int(row[3])
        self.name = str(row[4])
        self.date = optional_date(row[5]) # optional_date shouldn't return None for this table
        self.time = optional_time(row[6])
        return self

    raceId: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    round: Mapped[int] = mapped_column(Integer)
    circuitId: Mapped[int] = mapped_column(ForeignKey("circuit.circuitId"))
    name: Mapped[str] = mapped_column(String(128))
    date: Mapped[dt.date] = mapped_column(Date)
    time: Mapped[Optional[dt.time]] = mapped_column(Time)

    circuit: Mapped["Circuit"] = relationship("Circuit", foreign_keys=[circuitId])

class Constructor(db.Model):
    __tablename__ = "constructor"

    def from_csv(self, row):
        self.constructorId = int(row[0])
        self.constructorRef = str(row[1])
        self.name = str(row[2])
        self.nationality = str(row[3])
        return self

    constructorId: Mapped[int] = mapped_column(Integer, primary_key=True)
    constructorRef: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(64))
    nationality: Mapped[str] = mapped_column(String(64))

class Driver(db.Model):
    __tablename__ = "driver"

    def from_csv(self, row):
        self.driverId = int(row[0])
        self.driverRef = str(row[1])
        self.number = optional_int(row[2])
        self.code = str(row[3])
        self.forename = str(row[4])
        self.surname = str(row[5])
        self.dob = optional_date(row[6]) # optional_date shouldn't return None for this table
        self.nationality = str(row[7])
        return self

    driverId: Mapped[int] = mapped_column(Integer, primary_key=True)
    driverRef: Mapped[str] = mapped_column(String(64))
    number: Mapped[Optional[int]] = mapped_column(Integer)
    code: Mapped[str] = mapped_column(String(8))
    forename: Mapped[str] = mapped_column(String(32))
    surname: Mapped[str] = mapped_column(String(32))
    dob: Mapped[dt.date] = mapped_column(Date)
    nationality: Mapped[str] = mapped_column(String(32))

class Status(db.Model):
    __tablename__ = "status"

    def from_csv(self, row):
        self.statusId = int(row[0])
        self.status = str(row[1])
        return self

    statusId: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(32))

class Result(db.Model):
    __tablename__ = "result"

    def from_csv(self, row):
        self.resultId = int(row[0])
        self.raceId = int(row[1])
        self.driverId = int(row[2])
        self.constructorId = int(row[3])
        self.number = optional_int(row[4])
        self.grid = int(row[5])
        self.position = optional_int(row[6])
        self.positionText = str(row[7])
        self.positionOrder = int(row[8])
        self.points = str(row[9])
        self.laps = int(row[10])
        self.time = str(row[11])
        self.milliseconds = optional_int(row[12])
        self.fastestLap = optional_int(row[13])
        self.rank = optional_int(row[14])
        self.fastestLapTime = optional_time(row[15])
        self.fastestLapSpeed = optional_str(row[16])
        self.statusId = int(row[17])
        return self

    resultId: Mapped[int] = mapped_column(Integer, primary_key=True)
    raceId: Mapped[int] = mapped_column(ForeignKey("race.raceId"))
    driverId: Mapped[int] = mapped_column(ForeignKey("driver.driverId"))
    constructorId: Mapped[int] = mapped_column(ForeignKey("constructor.constructorId"))
    number: Mapped[Optional[int]] = mapped_column(Integer)
    grid: Mapped[int] = mapped_column(Integer)
    postition: Mapped[Optional[int]] = mapped_column(Integer)
    positionText: Mapped[str] = mapped_column(String(8))
    positionOrder: Mapped[int] = mapped_column(Integer)
    points: Mapped[str] = mapped_column(String(8))
    laps: Mapped[int] = mapped_column(Integer)
    time: Mapped[str] = mapped_column(String(16))
    milliseconds: Mapped[Optional[int]] = mapped_column(Integer)
    fastestLap: Mapped[Optional[int]] = mapped_column(Integer)
    rank: Mapped[Optional[int]] = mapped_column(Integer)
    fastestLapTime: Mapped[Optional[dt.time]] = mapped_column(Time)
    fastestLapSpeed: Mapped[Optional[str]] = mapped_column(String(16))
    statusId: Mapped[int] = mapped_column(ForeignKey("status.statusId"))

    race: Mapped["Race"] = relationship("Race", foreign_keys=[raceId])
    driver: Mapped["Driver"] = relationship("Driver", foreign_keys=[driverId])
    constructor: Mapped["Constructor"] = relationship("Constructor", foreign_keys=[constructorId])
    status: Mapped["Status"] = relationship("Status", foreign_keys=[statusId])


# # This table contains users that can guess
# class User(db.Model):
#     __tablename__ = "user"

#     def from_csv(self, row):
#         self.name   = str(row[0])
#         self.active = bool(row[1])
#         return self

#     name:   Mapped[str]  = mapped_column(String(32), primary_key=True)
#     active: Mapped[bool] = mapped_column(Boolean) # Only show active users

# # This table contains guesses made by users
# class Guess(db.Model):
#     __tablename__ = "guess"

#     def from_csv(self, row):
#         self.id            = int(row[0])
#         self.user_id       = str(row[1])
#         self.race_id       = str(row[2])
#         self.season_id     = int(row[3])
#         self.p10_id        = str(row[4])
#         self.dnf_id        = str(row[5])
#         self.raceresult_id = int(row[6])
#         return self

#     id:            Mapped[int]          = mapped_column(Integer, primary_key=True)
#     user_id:       Mapped[str]          = mapped_column(ForeignKey("user.name"))
#     race_id:       Mapped[str]          = mapped_column(ForeignKey("race.id"))
#     season_id:     Mapped[int]          = mapped_column(ForeignKey("season.year"))
#     p10_id:        Mapped[str]          = mapped_column(ForeignKey("driver.name"))
#     dnf_id:        Mapped[str]          = mapped_column(ForeignKey("driver.name"))
#     raceresult_id: Mapped[int]          = mapped_column(ForeignKey("raceresult.id"))

#     user:          Mapped["User"]       = relationship("User", foreign_keys=[user_id])
#     race:          Mapped["Race"]       = relationship("Race", foreign_keys=[race_id])
#     season:        Mapped["Season"]     = relationship("Season", foreign_keys=[season_id]) # Redundant but should make things easier
#     p10:           Mapped["Driver"]     = relationship("Driver", foreign_keys=[p10_id])
#     dnf:           Mapped["Driver"]     = relationship("Driver", foreign_keys=[dnf_id])
#     raceresult:    Mapped["RaceResult"] = relationship("RaceResult", foreign_keys=[raceresult_id])