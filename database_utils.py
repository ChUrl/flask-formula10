import csv
import os.path

from model import *


def load_csv(filename):
    if not os.path.exists(filename):
        print(f"Could not load data from file {filename}, as it doesn't exist!")
        return []

    with open(filename, "r", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        next(reader, None)  # skip header
        return list(reader)


def write_csv(filename, objects):
    if len(objects) == 0:
        print(f"Could not write objects to file {filename}, as no objects were given!")
        return

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(objects[0].__csv_header__)
        for obj in objects:
            writer.writerow(obj.to_csv())


# Reload static database data, this has to be called from the app context
def reload_static_data(db):
    print("Initializing Database with Static Values...")
    # Create it (if it doesn't exist!)
    db.create_all()

    # Clear static data
    Team.query.delete()
    Driver.query.delete()
    Race.query.delete()
    User.query.delete()

    # Reload static data
    for row in load_csv("static_data/teams.csv"):
        db.session.add(Team().from_csv(row))
    for row in load_csv("static_data/drivers.csv"):
        db.session.add(Driver().from_csv(row))
    for row in load_csv("static_data/races.csv"):
        db.session.add(Race().from_csv(row))
    for row in load_csv("static_data/users.csv"):
        db.session.add(User().from_csv(row))

    db.session.commit()


def reload_dynamic_data(db):
    print("Initializing Database with Dynamic Values...")

    # Clear dynamic data
    User.query.delete()
    RaceResult.query.delete()
    RaceGuess.query.delete()
    TeamWinners.query.delete()
    PodiumDrivers.query.delete()
    SeasonGuess.query.delete()

    # Reload dynamic data
    for row in load_csv("dynamic_data/users.csv"):
        db.session.add(User().from_csv(row))
    for row in load_csv("dynamic_data/raceresults.csv"):
        db.session.add(RaceResult().from_csv(row))
    for row in load_csv("dynamic_data/raceguesses.csv"):
        db.session.add(RaceGuess().from_csv(row))
    for row in load_csv("dynamic_data/teamwinners.csv"):
        db.session.add(TeamWinners().from_csv(row))
    for row in load_csv("dynamic_data/podiumdrivers.csv"):
        db.session.add(PodiumDrivers().from_csv(row))
    for row in load_csv("dynamic_data/seasonguesses.csv"):
        db.session.add(SeasonGuess().from_csv(row))

    db.session.commit()


def export_dynamic_data():
    print("Exporting Userdata...")

    users = User.query.all()
    raceresults = RaceResult.query.all()
    raceguesses = RaceGuess.query.all()
    teamwinners = TeamWinners.query.all()
    podiumdrivers = PodiumDrivers.query.all()
    seasonguesses = SeasonGuess.query.all()

    write_csv("dynamic_data/users.csv", users)
    write_csv("dynamic_data/raceresults.csv", raceresults)
    write_csv("dynamic_data/raceguesses.csv", raceguesses)
    write_csv("dynamic_data/teamwinners.csv", teamwinners)
    write_csv("dynamic_data/podiumdrivers.csv", podiumdrivers)
    write_csv("dynamic_data/seasonguesses.csv", seasonguesses)
