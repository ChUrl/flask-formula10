from urllib.parse import quote

from formula10.database.model.db_driver import DbDriver
from formula10.frontend.model.team import NONE_TEAM, Team


class Driver():
    @classmethod
    def from_db_driver(cls, db_driver: DbDriver):
        driver: Driver = cls()
        driver.name = db_driver.name
        driver.abbr = db_driver.abbr
        driver.country = db_driver.country_code
        driver.team = Team.from_db_team(db_driver.team)
        return driver

    def to_db_driver(self) -> DbDriver:
        db_driver: DbDriver = DbDriver(name=self.name)
        db_driver.abbr = self.abbr
        db_driver.country_code = self.country
        db_driver.team_name = self.team.name
        return db_driver

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Driver):
            return self.name == __value.name

        return NotImplemented

    name: str
    abbr: str
    country: str
    team: Team

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)


NONE_DRIVER: Driver = Driver()
NONE_DRIVER.name = "None"
NONE_DRIVER.abbr = "None"
NONE_DRIVER.country = "NO"
NONE_DRIVER.team = NONE_TEAM