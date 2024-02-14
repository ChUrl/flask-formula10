import csv
from model import *


def load_csv(filename):
    with open("data/" + filename + ".csv", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        next(reader, None)  # skip header
        return list(reader)


# @todo CSV-Writer
def write_csv(filename):
    with open("data/" + filename + ".csv", newline="") as file:
        writer = csv.writer(file, delimiter=",")


# @todo Complete CSV Files
# @todo Reload Static Data
# Reload static database data, this has to be called from the app context
def reload_static_data(db):
    print("Initializing DataBase with Static Values...")
    # Create it (if it doesn't exist!)
    db.create_all()

    # Clear static data
    Team.query.delete()
    Driver.query.delete()
    GrandPrix.query.delete()
    Race.query.delete()
    RaceResult.query.delete()
    User.query.delete()
    Guess.query.delete()

    # Reload static data
    for row in load_csv("teams"):
        db.session.add(Team().from_csv(row))
    for row in load_csv("drivers"):
        db.session.add(Driver().from_csv(row))
    for row in load_csv("grandsprix"):
        db.session.add(GrandPrix().from_csv(row))
    for row in load_csv("races"):
        db.session.add(Race().from_csv(row))
    for row in load_csv("raceresults"):
        db.session.add(RaceResult().from_csv(row))
    for row in load_csv("users"):
        db.session.add(User().from_csv(row))
    for row in load_csv("guesses"):
        db.session.add(Guess().from_csv(row))

    db.session.commit()


# @todo Export Dynamic Data
def export_dynamic_data():
    pass
