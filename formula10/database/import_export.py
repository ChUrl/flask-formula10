import csv
import os.path
from typing import List, Any

from formula10 import db
from formula10.database.model.db_driver import DbDriver
from formula10.database.model.db_race import DbRace
from formula10.database.model.db_race_guess import DbRaceGuess
from formula10.database.model.db_race_result import DbRaceResult
from formula10.database.model.db_season_guess import DbSeasonGuess
from formula10.database.model.db_season_guess_result import DbSeasonGuessResult
from formula10.database.model.db_team import DbTeam
from formula10.database.model.db_user import DbUser


def load_csv(filename: str) -> List[List[str]]:
    if not os.path.exists(filename):
        print(f"Could not load data from file {filename}, as it doesn't exist!")
        return []

    with open(filename, "r", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        next(reader, None)  # skip header
        return list(reader)


def write_csv(filename: str, objects: List[Any]):
    if len(objects) == 0:
        print(f"Could not write objects to file {filename}, as no objects were given!")
        return

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(objects[0].__csv_header__)
        for obj in objects:
            writer.writerow(obj.to_csv())


# Reload static database data, this has to be called from the app context
def reload_static_data():
    print("Initializing database with static values...")
    # Create it/update tables (if it/they doesn't exist!)
    db.create_all()

    # Clear static data
    db.session.query(DbTeam).delete()
    db.session.query(DbDriver).delete()
    db.session.query(DbRace).delete()

    # Reload static data
    for row in load_csv("data/static_import/teams.csv"):
        db.session.add(DbTeam.from_csv(row))
    for row in load_csv("data/static_import/drivers.csv"):
        db.session.add(DbDriver.from_csv(row))
    for row in load_csv("data/static_import/races.csv"):
        db.session.add(DbRace.from_csv(row))

    db.session.commit()


def reload_dynamic_data():
    print("Initializing database with dynamic values...")
    # Create it/update tables (if it/they doesn't exist!)
    db.create_all()

    # Clear dynamic data
    db.session.query(DbUser).delete()
    db.session.query(DbRaceResult).delete()
    db.session.query(DbRaceGuess).delete()
    db.session.query(DbSeasonGuess).delete()

    # Reload dynamic data
    for row in load_csv("data/dynamic_export/users.csv"):
        db.session.add(DbUser.from_csv(row))
    for row in load_csv("data/dynamic_export/raceresults.csv"):
        db.session.add(DbRaceResult.from_csv(row))
    for row in load_csv("data/dynamic_export/raceguesses.csv"):
        db.session.add(DbRaceGuess.from_csv(row))
    for row in load_csv("data/dynamic_export/seasonguesses.csv"):
        db.session.add(DbSeasonGuess.from_csv(row))

    db.session.commit()


def reload_season_guess_result_data():
    print("Loading season guess results...")
    # Create it/update tables (if it/they doesn't exist!)
    db.create_all()

    # Clear result data
    db.session.query(DbSeasonGuessResult).delete()

    # Reload result data
    for row in load_csv("data/static_import/season_guess_results.csv"):
        db.session.add(DbSeasonGuessResult.from_csv(row))

    db.session.commit()


def export_dynamic_data():
    print("Exporting Userdata...")

    users: List[DbUser] = db.session.query(DbUser).all()
    raceresults: List[DbRaceResult] = db.session.query(DbRaceResult).all()
    raceguesses: List[DbRaceGuess] = db.session.query(DbRaceGuess).all()
    seasonguesses: List[DbSeasonGuess] = db.session.query(DbSeasonGuess).all()

    write_csv("data/dynamic_export/users.csv", users)
    write_csv("data/dynamic_export/raceresults.csv", raceresults)
    write_csv("data/dynamic_export/raceguesses.csv", raceguesses)
    write_csv("data/dynamic_export/seasonguesses.csv", seasonguesses)
