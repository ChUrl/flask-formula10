from typing import List

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from model import *
from database_utils import reload_static_data, reload_dynamic_data, export_dynamic_data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# TODO
# - Sortable list to enter full race results (need 7 positions to calculate points),
#   don't enter race result on guess page
# - Move guessed place to leftmost column and display actual finishing position of driver instead
# - Choose "place to guess" late before the race?
# - Already show coming race in table, to give better feedback once a user has locked in a guess
# - Set fixed sizes for left- and rightmost column in races table
# - Fix the weird sizing everywhere when selecting only a single user...
# - Replace ALL absolute pixel values inside the templates


@app.route("/")
def index():
    return redirect("/race")


@app.route("/saveall")
def savedynamic():
    export_dynamic_data()
    return redirect("/")


@app.route("/loadall")
def load():
    reload_static_data(db)
    reload_dynamic_data(db)
    return redirect("/")


@app.route("/loadstatic")
def reloadstatic():
    reload_static_data(db)
    return redirect("/")


@app.route("/loaddynamic")
def reloaddynamic():
    reload_dynamic_data(db)
    return redirect("/")


@app.route("/race")
def guessraceresult():
    return redirect("/race/Everyone")


@app.route("/race/<username>")
def guessuserraceresults(username):
    users: List[User] = User.query.all()
    raceresults: List[RaceResult] = RaceResult.query.all()[::-1]
    drivers: List[Driver] = Driver.query.all()

    # Select User
    chosenusers = users
    if username != "Everyone":
        chosenusers = [user for user in users if user.name == username]

    pastguesses = dict()  # The guesses for which raceresults exist
    nextguesses = dict()  # The guesses that are still open for modification
    raceresult: RaceResult
    for raceresult in raceresults:
        pastguesses[raceresult.race_id] = dict()
    guess: RaceGuess
    for guess in RaceGuess.query.all():
        if guess.race_id in pastguesses:
            pastguesses[guess.race_id][guess.user_id] = guess
        else:
            nextguesses[guess.user_id] = guess

    # TODO: Getting by ID might be stupid, get by date instead?
    nextid = raceresults[0].race_id + 1 if len(raceresults) > 0 else 1
    nextrace: Race = Race.query.filter_by(id=nextid).first()

    return render_template("race.jinja",
                           users=users,
                           drivers=drivers,
                           raceresults=raceresults,
                           pastguesses=pastguesses,
                           currentselection=nextguesses,
                           nextrace=nextrace,
                           chosenusername=username,
                           chosenusers=chosenusers)


@app.route("/guessrace/<raceid>/<username>", methods=["POST"])
def guessrace(raceid, username):
    pxx = request.form.get("pxxselect")
    dnf = request.form.get("dnfselect")

    if pxx is None or dnf is None:
        return redirect("/race")

    if RaceResult.query.filter_by(race_id=raceid).first() is not None:
        print("Error: Can't guess race result if the race result is already known!")
        return redirect("/race")

    raceguess: RaceGuess | None = RaceGuess.query.filter_by(user_id=username, race_id=raceid).first()

    if raceguess is None:
        raceguess = RaceGuess()
        raceguess.user_id = username
        raceguess.race_id = raceid
        db.session.add(raceguess)

    raceguess.pxx_id = pxx
    raceguess.dnf_id = dnf
    db.session.commit()

    return redirect("/race")


@app.route("/enterresult/<raceid>", methods=["POST"])
def enterresult(raceid):
    pxx = request.form.get("pxxselect")
    dnf = request.form.get("dnfselect")

    if pxx is None or dnf is None:
        return redirect("/race")

    raceresult: RaceResult | None = RaceResult.query.filter_by(race_id=raceid).first()

    if raceresult is not None:
        print("RaceResult already exists!")
        return redirect("/race")

    raceresult = RaceResult()
    raceresult.race_id = raceid
    raceresult.pxx_id = pxx
    raceresult.dnf_id = dnf
    db.session.add(raceresult)
    db.session.commit()

    return redirect("/race")


@app.route("/season")
def guessseasonresults():
    return redirect("/season/Everyone")


@app.route("/season/<username>")
def guessuserseasonresults(username):
    users: List[User] = User.query.all()
    teams: List[Team] = Team.query.all()
    drivers: List[Driver] = Driver.query.all()

    # Remove NONE driver
    drivers = [driver for driver in drivers if driver.name != "NONE"]
    # Select User
    chosenusers = users
    if username != "Everyone":
        chosenusers = [user for user in users if user.name == username]

    seasonguesses = dict()
    guess: SeasonGuess
    for guess in SeasonGuess.query.all():
        seasonguesses[guess.user_id] = guess

    driverpairs = dict()
    team: Team
    for team in teams:
        driverpairs[team.name] = []
    driver: Driver
    for driver in drivers:
        driverpairs[driver.team.name] += [driver]

    return render_template("season.jinja",
                           users=users,
                           teams=teams,
                           drivers=drivers,
                           driverpairs=driverpairs,
                           currentselection=seasonguesses,
                           chosenusername=username,
                           chosenusers=chosenusers)


@app.route("/guessseason/<username>", methods=["POST"])
def guessseason(username):
    guesses = [
        request.form.get("hottakeselect"),
        request.form.get("p2select"),
        request.form.get("overtakeselect"),
        request.form.get("dnfselect"),
        request.form.get("gainedselect"),
        request.form.get("lostselect")
    ]
    teamwinnerguesses = [
        request.form.get(f"teamwinner-{team.name}") for team in Team.query.all()
    ]
    podiumdriverguesses = request.form.getlist("podiumdrivers")

    if any(guess is None for guess in guesses + teamwinnerguesses):
        print("Error: /guessseason could not obtain request data!")
        return redirect("/season")

    seasonguess: SeasonGuess | None = SeasonGuess.query.filter_by(user_id=username).first()
    teamwinners: TeamWinners | None = seasonguess.team_winners if seasonguess is not None else None
    podiumdrivers: PodiumDrivers | None = seasonguess.podium_drivers if seasonguess is not None else None

    if teamwinners is None:
        teamwinners = TeamWinners()
        db.session.add(teamwinners)

    teamwinners.winner_ids = teamwinnerguesses
    teamwinners.user_id = username
    db.session.commit()

    if podiumdrivers is None:
        podiumdrivers = PodiumDrivers()
        db.session.add(podiumdrivers)

    podiumdrivers.podium_ids = podiumdriverguesses
    podiumdrivers.user_id = username
    db.session.commit()

    # Refresh teamwinners + podiumdrivers to obtain IDs
    teamwinners = TeamWinners.query.filter_by(user_id=username).first()
    podiumdrivers = PodiumDrivers.query.filter_by(user_id=username).first()

    if seasonguess is None:
        seasonguess = SeasonGuess()
        seasonguess.user_id = username
        db.session.add(seasonguess)

    seasonguess.hot_take = guesses[0]
    seasonguess.p2_constructor_id = guesses[1]
    seasonguess.most_overtakes_id = guesses[2]
    seasonguess.most_dnfs_id = guesses[3]
    seasonguess.most_gained_id = guesses[4]
    seasonguess.most_lost_id = guesses[5]
    seasonguess.team_winners_id = teamwinners.id
    seasonguess.podium_drivers_id = podiumdrivers.id
    db.session.commit()

    return redirect("/season")


if __name__ == "__main__":
    app.run(debug=True)
