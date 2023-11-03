from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

# Modeling these entities separately should make it easier to add new guess categories, for example team guesses or GP guesses

# This table contains metainformation about the GPs, not specific to seasons (can be reused).
class GrandPrix(db.Model):
    __tablename__ = "grandprix"

    def from_csv(self, row):
        self.name         = str(row[0])
        self.country_code = str(row[1])
        return self

    name:         Mapped[str] = mapped_column(String(64), primary_key=True)
    country_code: Mapped[str] = mapped_column(String(2)) # alpha-2 code

# This table contains season information
class Season(db.Model):
    __tablename__ = "season"

    def from_csv(self, row):
        self.year   = int(row[0])
        self.active = bool(row[1])
        return self

    year:   Mapped[int]  = mapped_column(Integer, primary_key=True) # This is the year
    active: Mapped[bool] = mapped_column(Boolean) # Only allow guessing the current season

# This table contains manifestations of GPs, with dates
class Race(db.Model):
    __tablename__ = "race"

    def from_csv(self, row):
        self.id           = int(row[0])
        self.grandprix_id = str(row[1])
        self.season_id    = int(row[2])
        self.number       = int(row[3])
        self.date         = datetime.strptime(row[4], "%Y-%m-%d")
        return self

    id:           Mapped[int]         = mapped_column(Integer, primary_key=True)
    grandprix_id: Mapped[str]         = mapped_column(ForeignKey("grandprix.name"))
    season_id:    Mapped[int]         = mapped_column(ForeignKey("season.year"))
    number:       Mapped[int]         = mapped_column(Integer)
    date:         Mapped[datetime]    = mapped_column(DateTime)

    grandprix:    Mapped["GrandPrix"] = relationship("GrandPrix", foreign_keys=[grandprix_id])
    season:       Mapped["Season"]    = relationship("Season", foreign_keys=[season_id])

# This table contains teams, e.g. RedBull
class Team(db.Model):
    __tablename__ = "team"

    def from_csv(self, row):
        self.name         = str(row[0])
        self.country_code = str(row[1])
        return self

    name:         Mapped[str] = mapped_column(String(32), primary_key=True)
    country_code: Mapped[str] = mapped_column(String(2)) # alpha-2 code

# This table contains drivers and their team associations, e.g. Max Verschtappen
class Driver(db.Model):
    __tablename__ = "driver"

    def from_csv(self, row):
        self.name         = str(row[0])
        self.team_id      = str(row[1])
        self.country_code = str(row[2])
        self.active       = bool(row[3])
        return self

    name:         Mapped[str]    = mapped_column(String(32), primary_key=True)
    team_id:      Mapped[str]    = mapped_column(ForeignKey("team.name"))
    country_code: Mapped[str]    = mapped_column(String(2)) # alpha-2 code
    active:       Mapped[bool]   = mapped_column(Boolean) # Only allow guessing active drivers

    team:         Mapped["Team"] = relationship("Team", foreign_keys=[team_id])

class RaceResult(db.Model):
    __tablename__ = "raceresult"

    def from_csv(self, row):
        self.id        = int(row[0])
        self.race_id   = str(row[1])
        self.season_id = int(row[2])
        self.p10_id    = str(row[3])
        self.dnf_id    = str(row[4])
        return self

    id:        Mapped[int]      = mapped_column(Integer, primary_key=True)
    race_id:   Mapped[str]      = mapped_column(ForeignKey("race.id"))
    season_id: Mapped[int]      = mapped_column(ForeignKey("season.year"))

    # These map to drivers
    # p01_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p02_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p03_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p04_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p05_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p06_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p07_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p08_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p09_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    p10_id:    Mapped[str]      = mapped_column(ForeignKey("driver.name"))
    # p11_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p12_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p13_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p14_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p15_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p16_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p17_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p18_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p19_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    # p20_id:    Mapped[int]      = mapped_column(ForeignKey("driver.id"))
    dnf_id:    Mapped[str]      = mapped_column(ForeignKey("driver.name"))

    race:      Mapped["Race"]   = relationship("Race", foreign_keys=[race_id])
    season:    Mapped["Season"] = relationship("Season", foreign_keys=[season_id]) # Redundant but should make things easier

    # p01:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p01_id]) # Store all places to allow adding guesses
    # p02:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p02_id])
    # p03:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p03_id])
    # p04:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p04_id])
    # p05:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p05_id])
    # p06:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p06_id])
    # p07:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p07_id])
    # p08:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p08_id])
    # p09:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p09_id])
    p10:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p10_id])
    # p11:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p11_id])
    # p12:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p12_id])
    # p13:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p13_id])
    # p14:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p14_id])
    # p15:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p15_id])
    # p16:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p16_id])
    # p17:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p17_id])
    # p18:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p18_id])
    # p19:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p19_id])
    # p20:       Mapped["Driver"] = relationship("Driver", foreign_keys=[p20_id])
    dnf:       Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id]) # Only store first DNF

# This table contains users that can guess
class User(db.Model):
    __tablename__ = "user"

    def from_csv(self, row):
        self.name   = str(row[0])
        self.active = bool(row[1])
        return self

    name:   Mapped[str]  = mapped_column(String(32), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean) # Only show active users

# This table contains guesses made by users
class Guess(db.Model):
    __tablename__ = "guess"

    def from_csv(self, row):
        self.id            = int(row[0])
        self.user_id       = str(row[1])
        self.race_id       = str(row[2])
        self.season_id     = int(row[3])
        self.p10_id        = str(row[4])
        self.dnf_id        = str(row[5])
        self.raceresult_id = int(row[6])
        return self

    id:            Mapped[int]          = mapped_column(Integer, primary_key=True)
    user_id:       Mapped[str]          = mapped_column(ForeignKey("user.name"))
    race_id:       Mapped[str]          = mapped_column(ForeignKey("race.id"))
    season_id:     Mapped[int]          = mapped_column(ForeignKey("season.year"))
    p10_id:        Mapped[str]          = mapped_column(ForeignKey("driver.name"))
    dnf_id:        Mapped[str]          = mapped_column(ForeignKey("driver.name"))
    raceresult_id: Mapped[int]          = mapped_column(ForeignKey("raceresult.id"))

    user:          Mapped["User"]       = relationship("User", foreign_keys=[user_id])
    race:          Mapped["Race"]       = relationship("Race", foreign_keys=[race_id])
    season:        Mapped["Season"]     = relationship("Season", foreign_keys=[season_id]) # Redundant but should make things easier
    p10:           Mapped["Driver"]     = relationship("Driver", foreign_keys=[p10_id])
    dnf:           Mapped["Driver"]     = relationship("Driver", foreign_keys=[dnf_id])
    raceresult:    Mapped["RaceResult"] = relationship("RaceResult", foreign_keys=[raceresult_id])