from datetime import datetime
from urllib.parse import quote

from formula10.database.model.db_race import DbRace


class Race:
    @classmethod
    def from_db_race(cls, db_race: DbRace):
        race: Race = cls()
        race.id = db_race.id
        race.name = db_race.name
        race.number = db_race.number
        race.date = db_race.date
        race.place_to_guess = db_race.pxx
        race.quali_date = db_race.quali_date
        race.has_sprint = db_race.has_sprint
        return race

    def to_db_race(self) -> DbRace:
        db_race: DbRace = DbRace(id=self.id)
        db_race.name = self.name
        db_race.number = self.number
        db_race.date = self.date
        db_race.pxx = self.place_to_guess
        db_race.quali_date = self.date
        db_race.has_sprint = self.has_sprint
        return db_race

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Race):
            return self.id == __value.id

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)

    id: int
    name: str
    number: int
    date: datetime
    place_to_guess: int
    quali_date: datetime
    has_sprint: bool

    @property
    def name_sanitized(self) -> str:
        return quote(self.name)