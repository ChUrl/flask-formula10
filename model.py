from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


# This table contains users that can guess
class User(db.Model):
    __tablename__ = "user"

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


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


class Team(db.Model):
    __tablename__ = "team"

    def from_csv(self, row):
        self.name = str(row[0])
        return self

    name: Mapped[str] = mapped_column(String(32), primary_key=True)


# This table contains drivers and their team associations, e.g. Max Verschtappen
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

    def from_csv(self, row):
        self.id = int(row[0])
        self.race_id = str(row[1])
        self.p01_id = str(row[2])
        self.p02_id = str(row[3])
        self.p03_id = str(row[4])
        self.p04_id = str(row[5])
        self.p05_id = str(row[6])
        self.p06_id = str(row[7])
        self.p07_id = str(row[8])
        self.p08_id = str(row[9])
        self.p09_id = str(row[10])
        self.p10_id = str(row[11])
        self.p11_id = str(row[12])
        self.p12_id = str(row[13])
        self.p13_id = str(row[14])
        self.p14_id = str(row[15])
        self.p15_id = str(row[16])
        self.p16_id = str(row[17])
        self.p17_id = str(row[18])
        self.p18_id = str(row[19])
        self.p19_id = str(row[20])
        self.p20_id = str(row[21])
        self.dnf01_id = str(row[22])
        self.dnf02_id = str(row[23])
        self.dnf03_id = str(row[24])
        self.dnf04_id = str(row[25])
        self.dnf05_id = str(row[26])
        self.dnf06_id = str(row[27])
        self.dnf07_id = str(row[28])
        self.dnf08_id = str(row[29])
        self.dnf09_id = str(row[30])
        self.dnf10_id = str(row[31])
        self.dnf11_id = str(row[32])
        self.dnf12_id = str(row[33])
        self.dnf13_id = str(row[34])
        self.dnf14_id = str(row[35])
        self.dnf15_id = str(row[36])
        self.dnf16_id = str(row[37])
        self.dnf17_id = str(row[38])
        self.dnf18_id = str(row[39])
        self.dnf19_id = str(row[40])
        self.dnf20_id = str(row[41])
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    race_id: Mapped[str] = mapped_column(ForeignKey("race.id"))
    p01_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p02_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p03_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p04_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p05_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p06_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p07_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p08_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p09_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p10_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p11_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p12_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p13_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p14_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p15_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p16_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p17_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p18_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p19_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p20_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf01_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf02_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf03_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf04_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf05_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf06_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf07_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf08_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf09_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf10_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf11_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf12_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf13_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf14_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf15_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf16_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf17_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf18_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf19_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf20_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    p01: Mapped["Driver"] = relationship("Driver", foreign_keys=[p01_id])
    p02: Mapped["Driver"] = relationship("Driver", foreign_keys=[p02_id])
    p03: Mapped["Driver"] = relationship("Driver", foreign_keys=[p03_id])
    p04: Mapped["Driver"] = relationship("Driver", foreign_keys=[p04_id])
    p05: Mapped["Driver"] = relationship("Driver", foreign_keys=[p05_id])
    p06: Mapped["Driver"] = relationship("Driver", foreign_keys=[p06_id])
    p07: Mapped["Driver"] = relationship("Driver", foreign_keys=[p07_id])
    p08: Mapped["Driver"] = relationship("Driver", foreign_keys=[p08_id])
    p09: Mapped["Driver"] = relationship("Driver", foreign_keys=[p09_id])
    p10: Mapped["Driver"] = relationship("Driver", foreign_keys=[p10_id])
    p11: Mapped["Driver"] = relationship("Driver", foreign_keys=[p11_id])
    p12: Mapped["Driver"] = relationship("Driver", foreign_keys=[p12_id])
    p13: Mapped["Driver"] = relationship("Driver", foreign_keys=[p13_id])
    p14: Mapped["Driver"] = relationship("Driver", foreign_keys=[p14_id])
    p15: Mapped["Driver"] = relationship("Driver", foreign_keys=[p15_id])
    p16: Mapped["Driver"] = relationship("Driver", foreign_keys=[p16_id])
    p17: Mapped["Driver"] = relationship("Driver", foreign_keys=[p17_id])
    p18: Mapped["Driver"] = relationship("Driver", foreign_keys=[p18_id])
    p19: Mapped["Driver"] = relationship("Driver", foreign_keys=[p19_id])
    p20: Mapped["Driver"] = relationship("Driver", foreign_keys=[p20_id])
    dnf01: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf01_id])
    dnf02: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf02_id])
    dnf03: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf03_id])
    dnf04: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf04_id])
    dnf05: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf05_id])
    dnf06: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf06_id])
    dnf07: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf07_id])
    dnf08: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf08_id])
    dnf09: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf09_id])
    dnf10: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf10_id])
    dnf11: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf11_id])
    dnf12: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf12_id])
    dnf13: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf13_id])
    dnf14: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf14_id])
    dnf15: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf15_id])
    dnf16: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf16_id])
    dnf17: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf17_id])
    dnf18: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf18_id])
    dnf19: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf19_id])
    dnf20: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf20_id])


# Per race guesses: PX, DNF
# Per season guesses: Hot, P2 Constructor, Most overtakes, Most DNFs, Team winner,
#                     At least 1 podium


# This table contains race guesses made by users
class RaceGuess(db.Model):
    __tablename__ = "raceguess"

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.race_id = str(row[2])
        self.pXX_id = str(row[3])
        self.dnf_id = str(row[4])
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    race_id: Mapped[str] = mapped_column(ForeignKey("race.id"))
    pXX_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    pXX: Mapped["Driver"] = relationship("Driver", foreign_keys=[pXX_id])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])


class SeasonGuess(db.Model):
    __tablename__ = "seasonguess"

    def from_csv(self, row):
        return self

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    hot_take: Mapped[str] = mapped_column(String(512))
