from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


# This table contains manifestations of GPs, with dates
class Race(db.Model):
    __tablename__ = "race"

    def from_csv(self, row):
        self.id = int(row[0])
        self.grandprix = str(row[1])
        self.number = int(row[2])
        self.date = datetime.strptime(row[3], "%Y-%m-%d")
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    grandprix: Mapped[str] = mapped_column(String(32))

    number: Mapped[int] = mapped_column(Integer)

    date: Mapped[datetime] = mapped_column(DateTime)


# This table contains drivers and their team associations, e.g. Max Verschtappen
class Driver(db.Model):
    __tablename__ = "driver"

    def from_csv(self, row):
        self.name = str(row[0])
        self.team = str(row[1])
        self.country_code = str(row[2])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)

    team: Mapped[str] = mapped_column(String(32))

    country_code: Mapped[str] = mapped_column(String(2))  # alpha-2 code


class RaceResult(db.Model):
    __tablename__ = "raceresult"

    def from_csv(self, row):
        self.id = int(row[0])
        self.race_id = str(row[1])
        self.p10_id = str(row[2])
        self.dnf_id = str(row[3])
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    race_id: Mapped[str] = mapped_column(ForeignKey("race.id"))
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])

    p10_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p10: Mapped["Driver"] = relationship("Driver", foreign_keys=[p10_id])

    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])  # Only store first DNF


# This table contains users that can guess
class User(db.Model):
    __tablename__ = "user"

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


# Per race guesses: PX, DNF
# Per season guesses: Hot, P2 Constructor, Most overtakes, Most DNFs, Team winner,
#                     At least 1 podium


# This table contains guesses made by users
class Guess(db.Model):
    __tablename__ = "guess"

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.race_id = str(row[2])
        self.p10_id = str(row[3])
        self.dnf_id = str(row[4])
        self.raceresult_id = int(row[5])
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    race_id: Mapped[str] = mapped_column(ForeignKey("race.id"))
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])

    p10_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p10: Mapped["Driver"] = relationship("Driver", foreign_keys=[p10_id])

    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])

    raceresult_id: Mapped[int] = mapped_column(ForeignKey("raceresult.id"))
    raceresult: Mapped["RaceResult"] = relationship("RaceResult", foreign_keys=[raceresult_id])
