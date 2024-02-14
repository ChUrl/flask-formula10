from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


class Race(db.Model):
    __tablename__ = "race"

    def from_csv(self, row):
        self.id = int(row[0])
        self.grandprix = str(row[1])
        self.number = int(row[2])
        self.date = datetime.strptime(row[3], "%Y-%m-%d")
        self.pxx = int(row[4])
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


class RaceResult(db.Model):
    __tablename__ = "raceresult"
    __csv_header__ = ["id", "race_id", "pxx_id", "dnf_id"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.race_id = str(row[1])
        self.pxx_id = str(row[2])
        self.dnf_id = str(row[22])
        return self

    def to_csv(self):
        return [
            self.id,
            self.race_id,
            self.pxx_id,
            self.dnf_id
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    race_id: Mapped[str] = mapped_column(ForeignKey("race.id"))
    pxx_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    pxx: Mapped["Driver"] = relationship("Driver", foreign_keys=[pxx_id])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])


# Per race guesses: PX, DNF
# Per season guesses: Hot, P2 Constructor, Most overtakes, Most DNFs, Team winner,
#                     At least 1 podium


# This table contains race guesses made by users
class RaceGuess(db.Model):
    __tablename__ = "raceguess"
    __csv_header__ = ["id", "user_id", "race_id", "pxx_id", "dnf_id"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.race_id = str(row[2])
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
    race_id: Mapped[str] = mapped_column(ForeignKey("race.id"))
    pxx_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    pxx: Mapped["Driver"] = relationship("Driver", foreign_keys=[pxx_id])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])


class SeasonGuess(db.Model):
    __tablename__ = "seasonguess"
    __csv_header__ = ["id", "user_id", "hot_take"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.hot_take = str(row[2])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.hot_take
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    hot_take: Mapped[str] = mapped_column(String(512))
