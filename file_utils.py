import csv
import os.path
from typing import List, Any
from model import Team, Driver, Race, User, RaceResult, RaceGuess, TeamWinners, PodiumDrivers, SeasonGuess, db


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
    print("Initializing Database with Static Values...")
    # Create it (if it doesn't exist!)
    db.create_all()

    # Clear static data
    db.session.query(Team).delete()
    db.session.query(Driver).delete()
    db.session.query(Race).delete()

    # Reload static data
    for row in load_csv("static_data/teams.csv"):
        db.session.add(Team.from_csv(row))
    for row in load_csv("static_data/drivers.csv"):
        db.session.add(Driver.from_csv(row))
    for row in load_csv("static_data/races.csv"):
        db.session.add(Race.from_csv(row))

    db.session.commit()


def reload_dynamic_data():
    print("Initializing Database with Dynamic Values...")
    # Create it (if it doesn't exist!)
    db.create_all()

    # Clear dynamic data
    db.session.query(User).delete()
    db.session.query(RaceResult).delete()
    db.session.query(RaceGuess).delete()
    db.session.query(TeamWinners).delete()
    db.session.query(PodiumDrivers).delete()
    db.session.query(SeasonGuess).delete()

    # Reload dynamic data
    for row in load_csv("dynamic_data/users.csv"):
        db.session.add(User.from_csv(row))
    for row in load_csv("dynamic_data/raceresults.csv"):
        db.session.add(RaceResult.from_csv(row))
    for row in load_csv("dynamic_data/raceguesses.csv"):
        db.session.add(RaceGuess.from_csv(row))
    for row in load_csv("dynamic_data/teamwinners.csv"):
        db.session.add(TeamWinners.from_csv(row))
    for row in load_csv("dynamic_data/podiumdrivers.csv"):
        db.session.add(PodiumDrivers.from_csv(row))
    for row in load_csv("dynamic_data/seasonguesses.csv"):
        db.session.add(SeasonGuess.from_csv(row))

    db.session.commit()


def export_dynamic_data():
    print("Exporting Userdata...")

    users: List[User] = db.session.query(User).all()
    raceresults: List[RaceResult] = db.session.query(RaceResult).all()
    raceguesses: List[RaceGuess] = db.session.query(RaceGuess).all()
    teamwinners: List[TeamWinners] = db.session.query(TeamWinners).all()
    podiumdrivers: List[PodiumDrivers] = db.session.query(PodiumDrivers).all()
    seasonguesses: List[SeasonGuess] = db.session.query(SeasonGuess).all()

    write_csv("dynamic_data/users.csv", users)
    write_csv("dynamic_data/raceresults.csv", raceresults)
    write_csv("dynamic_data/raceguesses.csv", raceguesses)
    write_csv("dynamic_data/teamwinners.csv", teamwinners)
    write_csv("dynamic_data/podiumdrivers.csv", podiumdrivers)
    write_csv("dynamic_data/seasonguesses.csv", seasonguesses)
