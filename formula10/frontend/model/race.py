from datetime import datetime
from urllib.parse import quote

from formula10.database.model.db_race import DbRace


class Race():
    @classmethod
    def from_db_race(cls, db_race: DbRace):
        race: Race = cls()
        race.name = db_race.name
        race.number = db_race.number
        race.date = db_race.date
        race.place_to_guess = db_race.pxx
        return race

    def to_db_race(self) -> DbRace:
        db_race: DbRace = DbRace(name=self.name,
                                 number=self.number,
                                 date=self.date,
                                 pxx=self.place_to_guess)
        return db_race

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Race):
            return self.name == __value.name

        return NotImplemented

    name: str
    number: int
    date: datetime
    place_to_guess: int

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)