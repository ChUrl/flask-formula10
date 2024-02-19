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
# General
# - Store standing/dnf orders as dicts, since lists lose their order
# - Make user headers in race table clickable, to reach the specific page. Do the same for the season cards
# - When showing correct guesses in green, show semi-correct ones in a weaker tone (probably need to prepare those here, instead of in the template)
# - Also show previous race results, and allow to change them. Or at least, allow editing the current one and show current state (do it like the activeuser select for results)
# - Remove whitespace from usernames + races. Sanitization should only happen inside the templates + endpoint controllers, for the URLs
# - Add doc comments to model

# - Make the season card grid left-aligned? So e.g. 2 cards are not spread over the whole screen with large gaps?
# - Choose "place to guess" late before the race?
# - Timer until season picks lock + next race timer
# - A lot of validation (esp. in the model), each input should be checked...

# Statistics page
# - Auto calculate points
# - Generate static diagram using chart.js + templating the js (funny yikes)

# Rules page


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
    activeuser: User | None = User.query.filter_by(name=username).first()  # "Everyone" should yield None
    raceresults: List[RaceResult] = RaceResult.query.all()[::-1]
    drivers: List[Driver] = Driver.query.all()

    print(raceresults)

    guesses: Dict[int, Dict[str, RaceGuess]] = dict()
    guess: RaceGuess
    for guess in RaceGuess.query.all():
        if guess.race_id not in guesses:
            guesses[guess.race_id] = dict()

        guesses[guess.race_id][guess.user_id] = guess

    nextid = raceresults[0].race_id + 1 if len(raceresults) > 0 else 1
    nextrace: Race | None = Race.query.filter_by(id=nextid).first()

    return render_template("race.jinja",
                           users=users,
                           drivers=drivers,
                           raceresults=raceresults,
                           guesses=guesses,
                           activeuser=activeuser,
                           currentrace=nextrace)


@app.route("/guessrace/<raceid>/<username>", methods=["POST"])
def guessrace(raceid, username):
    pxx: str | None = request.form.get("pxxselect")
    dnf: str | None = request.form.get("dnfselect")

    if pxx is None or dnf is None:
        return redirect(f"/race/{username}")

    if RaceResult.query.filter_by(race_id=raceid).first() is not None:
        print("Error: Can't guess race result if the race result is already known!")
        return redirect(f"/race/{username}")

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


@app.route("/season")
def guessseasonresults():
    return redirect("/season/Everyone")


@app.route("/season/<username>")
def guessuserseasonresults(username):
    users: List[User] = User.query.all()
    activeuser: User | None = User.query.filter_by(name=username).first()
    teams: List[Team] = Team.query.all()
    drivers: List[Driver] = Driver.query.all()

    # Remove NONE driver
    drivers = [driver for driver in drivers if driver.name != "NONE"]

    guesses: Dict[str, SeasonGuess] = dict()
    guess: SeasonGuess
    for guess in SeasonGuess.query.all():
        guesses[guess.user_id] = guess

    driverpairs: Dict[str, List[Driver]] = dict()
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
                           guesses=guesses,
                           activeuser=activeuser)


@app.route("/guessseason/<username>", methods=["POST"])
def guessseason(username: str):
    guesses: List[str | None] = [
        request.form.get("hottakeselect"),
        request.form.get("p2select"),
        request.form.get("overtakeselect"),
        request.form.get("dnfselect"),
        request.form.get("gainedselect"),
        request.form.get("lostselect")
    ]
    teamwinnerguesses: List[str | None] = [
        request.form.get(f"teamwinner-{team.name}") for team in Team.query.all()
    ]
    podiumdriverguesses: List[str] = request.form.getlist("podiumdrivers")

    if any(guess is None for guess in guesses + teamwinnerguesses):
        print("Error: /guessseason could not obtain request data!")
        return redirect("/season")

    seasonguess: SeasonGuess | None = SeasonGuess.query.filter_by(user_id=username).first()
    teamwinners: TeamWinners | None = seasonguess.team_winners if seasonguess is not None else None
    podiumdrivers: PodiumDrivers | None = seasonguess.podium_drivers if seasonguess is not None else None

    if teamwinners is None:
        teamwinners = TeamWinners()
        db.session.add(teamwinners)

    teamwinners.winner_ids = teamwinnerguesses  # Pylance throws error, but nullcheck is done
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

    seasonguess.hot_take = guesses[0]  # Pylance throws error but nullcheck is done
    seasonguess.p2_constructor_id = guesses[1]  # Pylance throws error but nullcheck is done
    seasonguess.most_overtakes_id = guesses[2]  # Pylance throws error but nullcheck is done
    seasonguess.most_dnfs_id = guesses[3]  # Pylance throws error but nullcheck is done
    seasonguess.most_gained_id = guesses[4]  # Pylance throws error but nullcheck is done
    seasonguess.most_lost_id = guesses[5]  # Pylance throws error but nullcheck is done
    seasonguess.team_winners_id = teamwinners.id  # Pylance throws error but nullcheck is done
    seasonguess.podium_drivers_id = podiumdrivers.id  # Pylance throws error but nullcheck is done
    db.session.commit()

    return redirect("/season")


@app.route("/enter")
def entercurrentraceresult():
    return redirect("/enter/Current")


@app.route("/enter/<resultname>")
def enterraceresult(resultname: str):
    drivers: List[Driver] = Driver.query.all()
    raceresults: List[RaceResult] = RaceResult.query.all()[::-1]

    # Find next race without result
    nextid = raceresults[0].race_id + 1 if len(raceresults) > 0 else 1
    nextrace: Race | None = Race.query.filter_by(id=nextid).first()

    activeresult: RaceResult | None = None
    if resultname != "Current":
        # Obtain the chosen result
        activeresult = list(filter(lambda result: result.race.grandprix == resultname, raceresults))[0]
    else:
        # Obtain the current result if it exists
        activeresult = raceresults[0] if len(raceresults) > 0 and raceresults[0].race_id == nextrace else None

    # Remove NONE driver
    drivers = [driver for driver in drivers if driver.name != "NONE"]

    return render_template("enter.jinja",
                           drivers=drivers,
                           race=nextrace,
                           results=raceresults,
                           activeresult=activeresult)


@app.route("/enterresult/<raceid>", methods=["POST"])
def enterresult(raceid):
    pxxs: List[str] = request.form.getlist("pxxdrivers")
    dnfs: List[str] = request.form.getlist("dnf-drivers")
    excludes: List[str] = request.form.getlist("exclude-drivers")

    # Use strings as keys, as these dicts will be serialized to json
    pxxs_dict: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxxs)}
    dnfs_dict: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxxs) if driver in dnfs}

    print(pxxs_dict)

    raceresult: RaceResult | None = RaceResult.query.filter_by(race_id=raceid).first()

    if raceresult is None:
        raceresult = RaceResult()
        db.session.add(raceresult)

    raceresult.race_id = raceid
    raceresult.pxx_ids = pxxs_dict
    raceresult.dnf_ids = dnfs_dict if len(dnfs) > 0 else {"20": "NONE"}
    raceresult.exclude_ids = excludes
    db.session.commit()

    race: Race | None = Race.query.filter_by(id=raceid).first()
    if race is None:
        print("Error: Can't redirect to /enter/<GrandPrix> because race couldn't be found")
        return redirect("/enter")

    return redirect(f"/enter/{race.grandprix}")


@app.route("/users")
def manageusers():
    users: List[User] = User.query.all()

    return render_template("users.jinja",
                           users=users)


@app.route("/adduser", methods=["POST"])
def adduser():
    username: str | None = request.form.get("select-add-user")

    if username is None or len(username) == 0:
        print(f"Not adding user, since no username was received")
        return redirect("/users")

    if len(User.query.filter_by(name=username).all()) > 0:
        print(f"Not adding user {username}: Already exists!")
        return redirect("/users")

    user = User()
    user.name = username
    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route("/deleteuser", methods=["POST"])
def deleteuser():
    username = request.form.get("select-delete-user")

    if username is None or len(username) == 0:
        print(f"Not deleting user, since no username was received")
        return redirect("/users")

    if username == "Select User":
        return redirect("/users")

    print(f"Deleting user {username}...")

    User.query.filter_by(name=username).delete()
    db.session.commit()

    return redirect("/users")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
