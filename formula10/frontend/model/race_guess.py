from formula10.database.model.db_race_guess import DbRaceGuess
from formula10.frontend.model.driver import Driver
from formula10.frontend.model.race import Race
from formula10.frontend.model.user import User


class RaceGuess():
    @classmethod
    def from_db_race_guess(cls, db_race_guess: DbRaceGuess):
        race_guess: RaceGuess = cls()
        race_guess.user = User.from_db_user(db_race_guess.user)
        race_guess.race = Race.from_db_race(db_race_guess.race)
        race_guess.pxx_guess = Driver.from_db_driver(db_race_guess.pxx)
        race_guess.dnf_guess = Driver.from_db_driver(db_race_guess.dnf)
        return race_guess

    def to_db_race_guess(self) -> DbRaceGuess:
        db_race_guess: DbRaceGuess = DbRaceGuess(user_name=self.user.name,
                                                 race_name=self.race.name,
                                                 pxx_driver_name=self.pxx_guess.name,
                                                 dnf_driver_name=self.dnf_guess.name)
        return db_race_guess

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, RaceGuess):
            return self.user == __value.user and self.race == __value.race

        return NotImplemented

    user: User
    race: Race
    pxx_guess: Driver
    dnf_guess: Driver
