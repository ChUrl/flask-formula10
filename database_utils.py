import csv
from model import *


def load_csv(filename):
    with open("init_data/" + filename + ".csv", "r", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        next(reader, None)  # skip header
        return list(reader)


# @todo CSV-Writer
def write_csv(filename, objects):
    with open("dynamic_data/" + filename + ".csv", "w", newline="") as file:
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
    for row in load_csv("teams"):
        db.session.add(Team().from_csv(row))
    for row in load_csv("drivers"):
        db.session.add(Driver().from_csv(row))
    for row in load_csv("races"):
        db.session.add(Race().from_csv(row))
    for row in load_csv("users"):
        db.session.add(User().from_csv(row))

    db.session.commit()


def export_dynamic_data():
    print("Exporting Userdata...")

    raceresults = RaceResult.query.all()
    raceguesses = RaceGuess.query.all()
    seasonguesses = SeasonGuess.query.all()

    if len(raceresults) > 0:
        write_csv("raceresults", raceresults)
    if len(raceguesses) > 0:
        write_csv("raceguesses", raceguesses)
    if len(seasonguesses) > 0:
        write_csv("seasonguesses", seasonguesses)
