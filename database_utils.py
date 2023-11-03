import csv
from model import *

def load_csv(filename):
    with open("data/" + filename + ".csv", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        next(reader, None) # skip header
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
    Circuit.query.delete()
    Constructor.query.delete()
    Driver.query.delete()
    Race.query.delete()
    Season.query.delete()

    # Reload static data
    for row in load_csv("circuits"):
        db.session.add(Circuit().from_csv(row))
    for row in load_csv("constructors"):
        db.session.add(Constructor().from_csv(row))
    for row in load_csv("drivers"):
        db.session.add(Driver().from_csv(row))
    for row in load_csv("races"):
        db.session.add(Race().from_csv(row))
    for row in load_csv("seasons"):
        db.session.add(Season().from_csv(row))
    for row in load_csv("status"):
        db.session.add(Status().from_csv(row))
    for row in load_csv("results"):
        db.session.add(Result().from_csv(row))

    db.session.commit()

# @todo Export Dynamic Data
def export_dynamic_data():
    pass