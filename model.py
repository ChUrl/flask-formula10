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


class RaceResult(db.Model):
    __tablename__ = "raceresult"
    __csv_header__ = ["id", "race_id", "pxx_id", "dnf_id"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.race_id = int(row[1])
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
    race_id: Mapped[int] = mapped_column(ForeignKey("race.id"))
    pxx_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    dnf_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    race: Mapped["Race"] = relationship("Race", foreign_keys=[race_id])
    pxx: Mapped["Driver"] = relationship("Driver", foreign_keys=[pxx_id])
    dnf: Mapped["Driver"] = relationship("Driver", foreign_keys=[dnf_id])


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


# Per season guesses: Hot, P2 Constructor, Most overtakes, Most DNFs, Team winner,
#                     At least 1 podium


class TeamWinners(db.Model):
    __tablename__ = "teamwinners"
    __csv_header__ = ["id", "user_id", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.a_id = str(row[2])
        self.b_id = str(row[3])
        self.c_id = str(row[4])
        self.d_id = str(row[5])
        self.e_id = str(row[6])
        self.f_id = str(row[7])
        self.g_id = str(row[8])
        self.h_id = str(row[9])
        self.i_id = str(row[10])
        self.j_id = str(row[11])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.a_id,
            self.b_id,
            self.c_id,
            self.d_id,
            self.e_id,
            self.f_id,
            self.g_id,
            self.h_id,
            self.i_id,
            self.j_id
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    a_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    b_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    c_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    d_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    e_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    f_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    g_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    h_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    i_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    j_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    a: Mapped["Driver"] = relationship("Driver", foreign_keys=[a_id])
    b: Mapped["Driver"] = relationship("Driver", foreign_keys=[b_id])
    c: Mapped["Driver"] = relationship("Driver", foreign_keys=[c_id])
    d: Mapped["Driver"] = relationship("Driver", foreign_keys=[d_id])
    e: Mapped["Driver"] = relationship("Driver", foreign_keys=[e_id])
    f: Mapped["Driver"] = relationship("Driver", foreign_keys=[f_id])
    g: Mapped["Driver"] = relationship("Driver", foreign_keys=[g_id])
    h: Mapped["Driver"] = relationship("Driver", foreign_keys=[h_id])
    i: Mapped["Driver"] = relationship("Driver", foreign_keys=[i_id])
    j: Mapped["Driver"] = relationship("Driver", foreign_keys=[j_id])


class PodiumDrivers(db.Model):
    __tablename__ = "podiumdrivers"
    __csv_header__ = ["id", "user_id", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.a_id = str(row[2])
        self.b_id = str(row[3])
        self.c_id = str(row[4])
        self.d_id = str(row[5])
        self.e_id = str(row[6])
        self.f_id = str(row[7])
        self.g_id = str(row[8])
        self.h_id = str(row[9])
        self.i_id = str(row[10])
        self.j_id = str(row[11])
        self.k_id = str(row[12])
        self.l_id = str(row[13])
        self.m_id = str(row[14])
        self.n_id = str(row[15])
        self.o_id = str(row[16])
        self.p_id = str(row[17])
        self.q_id = str(row[18])
        self.r_id = str(row[19])
        self.s_id = str(row[20])
        self.t_id = str(row[21])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.a_id,
            self.b_id,
            self.c_id,
            self.d_id,
            self.e_id,
            self.f_id,
            self.g_id,
            self.h_id,
            self.i_id,
            self.j_id,
            self.k_id,
            self.l_id,
            self.m_id,
            self.n_id,
            self.o_id,
            self.p_id,
            self.q_id,
            self.r_id,
            self.s_id,
            self.t_id
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    a_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    b_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    c_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    d_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    e_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    f_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    g_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    h_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    i_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    j_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    k_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    l_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    m_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    n_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    o_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    p_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    q_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    r_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    s_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    t_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    a: Mapped["Driver"] = relationship("Driver", foreign_keys=[a_id])
    b: Mapped["Driver"] = relationship("Driver", foreign_keys=[b_id])
    c: Mapped["Driver"] = relationship("Driver", foreign_keys=[c_id])
    d: Mapped["Driver"] = relationship("Driver", foreign_keys=[d_id])
    e: Mapped["Driver"] = relationship("Driver", foreign_keys=[e_id])
    f: Mapped["Driver"] = relationship("Driver", foreign_keys=[f_id])
    g: Mapped["Driver"] = relationship("Driver", foreign_keys=[g_id])
    h: Mapped["Driver"] = relationship("Driver", foreign_keys=[h_id])
    i: Mapped["Driver"] = relationship("Driver", foreign_keys=[i_id])
    j: Mapped["Driver"] = relationship("Driver", foreign_keys=[j_id])
    k: Mapped["Driver"] = relationship("Driver", foreign_keys=[k_id])
    l: Mapped["Driver"] = relationship("Driver", foreign_keys=[l_id])
    m: Mapped["Driver"] = relationship("Driver", foreign_keys=[m_id])
    n: Mapped["Driver"] = relationship("Driver", foreign_keys=[n_id])
    o: Mapped["Driver"] = relationship("Driver", foreign_keys=[o_id])
    p: Mapped["Driver"] = relationship("Driver", foreign_keys=[p_id])
    q: Mapped["Driver"] = relationship("Driver", foreign_keys=[q_id])
    r: Mapped["Driver"] = relationship("Driver", foreign_keys=[r_id])
    s: Mapped["Driver"] = relationship("Driver", foreign_keys=[s_id])
    t: Mapped["Driver"] = relationship("Driver", foreign_keys=[t_id])


class SeasonGuess(db.Model):
    __tablename__ = "seasonguess"
    __csv_header__ = ["id", "user_id",
                      "hot_take", "p2_constructor", "most_overtakes", "most_dnfs", "team_winners", "podium_drivers"]

    def from_csv(self, row):
        self.id = int(row[0])
        self.user_id = str(row[1])
        self.hot_take = str(row[2])
        self.p2_constructor_id = str(row[3])
        self.most_overtakes_id = str(row[4])
        self.most_dnfs_id = str(row[5])
        self.team_winners_id = int(row[6])
        self.podium_drivers_id = int(row[6])
        return self

    def to_csv(self):
        return [
            self.id,
            self.user_id,
            self.hot_take,
            self.p2_constructor_id,
            self.most_overtakes_id,
            self.most_dnfs_id,
            self.team_winners_id,
            self.podium_drivers_id
        ]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.name"))
    hot_take: Mapped[str] = mapped_column(String(512))
    p2_constructor_id: Mapped[str] = mapped_column(ForeignKey("team.name"))
    most_overtakes_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    most_dnfs_id: Mapped[str] = mapped_column(ForeignKey("driver.name"))
    team_winners_id: Mapped[int] = mapped_column(ForeignKey("teamwinners.id"))
    podium_drivers_id: Mapped[int] = mapped_column(ForeignKey("podiumdrivers.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    p2_constructor: Mapped["Team"] = relationship("Team", foreign_keys=[p2_constructor_id])
    most_overtakes: Mapped["Driver"] = relationship("Driver", foreign_keys=[most_overtakes_id])
    most_dnfs: Mapped["Driver"] = relationship("Driver", foreign_keys=[most_dnfs_id])
    team_winners: Mapped["TeamWinners"] = relationship("TeamWinners", foreign_keys=[team_winners_id])
    podium_drivers: Mapped["PodiumDrivers"] = relationship("PodiumDrivers", foreign_keys=[podium_drivers_id])
