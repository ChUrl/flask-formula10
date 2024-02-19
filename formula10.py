from flask import Flask, render_template, request, redirect
from model import *
from database_utils import reload_static_data, reload_dynamic_data, export_dynamic_data
from template_model import TemplateModel

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# TODO
# General

# - Sanitize URLs
# - A lot of validation (esp. in the model), each input should be checked...

# - Show cards of previous race results, like with season guesses?
# - Make the season card grid left-aligned? So e.g. 2 cards are not spread over the whole screen with large gaps?
# - Choose "place to guess" late before the race?

# Statistics page
# - Auto calculate points
# - Generate static diagram using chart.js + templating the js (funny yikes)

# Rules page


@app.route("/")
def root():
    return race_active_user("Everyone")


@app.route("/save/all", strict_slashes=False)
def save():
    export_dynamic_data()
    return redirect("/")


@app.route("/load/all")
def load():
    reload_static_data(db)
    reload_dynamic_data(db)
    return redirect("/")


@app.route("/load/static")
def load_static():
    reload_static_data(db)
    return redirect("/")


@app.route("/load/dynamic")
def load_dynamic():
    reload_dynamic_data(db)
    return redirect("/")


@app.route("/race")
def race_root():
    return redirect("/race/Everyone")


@app.route("/race/<user_name>")
def race_active_user(user_name: str):
    model = TemplateModel()
    return render_template("race.jinja",
                           active_user=model.user_by(user_name=user_name, ignore=["Everyone"]),
                           model=model)


@app.route("/race-guess/<race_name>/<user_name>", methods=["POST"])
def race_guess_post(race_name: str, user_name: str):
    pxx: str | None = request.form.get("pxxselect")
    dnf: str | None = request.form.get("dnfselect")

    if pxx is None or dnf is None:
        return race_active_user(user_name)

    if RaceResult.query.filter_by(race_name=race_name).first() is not None:
        print("Error: Can't guess race result if the race result is already known!")
        return redirect(f"/race/{user_name}")

    raceguess: RaceGuess | None = RaceGuess.query.filter_by(user_name=user_name, race_name=race_name).first()

    if raceguess is None:
        raceguess = RaceGuess()
        raceguess.user_name = user_name
        raceguess.race_name = race_name
        db.session.add(raceguess)

    raceguess.pxx_driver_name = pxx
    raceguess.dnf_driver_name = dnf
    db.session.commit()

    return redirect("/race/Everyone")


@app.route("/season")
def season_root():
    return redirect("/season/Everyone")


@app.route("/season/<user_name>")
def season_active_user(user_name: str):
    model = TemplateModel()
    return render_template("season.jinja",
                           active_user=model.user_by(user_name=user_name, ignore=["Everyone"]),
                           model=model)


@app.route("/season-guess/<user_name>", methods=["POST"])
def season_guess_post(user_name: str):
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
        return redirect(f"/season/{user_name}")

    seasonguess: SeasonGuess | None = SeasonGuess.query.filter_by(user_name=user_name).first()
    teamwinners: TeamWinners | None = seasonguess.team_winners if seasonguess is not None else None
    podiumdrivers: PodiumDrivers | None = seasonguess.podium_drivers if seasonguess is not None else None

    if teamwinners is None:
        teamwinners = TeamWinners()
        db.session.add(teamwinners)

    teamwinners.user_name = user_name
    teamwinners.teamwinner_driver_names = teamwinnerguesses  # Pylance throws error, but nullcheck is done
    db.session.commit()

    if podiumdrivers is None:
        podiumdrivers = PodiumDrivers()
        db.session.add(podiumdrivers)

    podiumdrivers.podium_driver_names = podiumdriverguesses
    podiumdrivers.user_name = user_name
    db.session.commit()

    if seasonguess is None:
        seasonguess = SeasonGuess()
        seasonguess.user_name = user_name
        db.session.add(seasonguess)

    seasonguess.hot_take = guesses[0]  # Pylance throws error but nullcheck is done
    seasonguess.p2_team_name = guesses[1]  # Pylance throws error but nullcheck is done
    seasonguess.overtake_driver_name = guesses[2]  # Pylance throws error but nullcheck is done
    seasonguess.dnf_driver_name = guesses[3]  # Pylance throws error but nullcheck is done
    seasonguess.gained_driver_name = guesses[4]  # Pylance throws error but nullcheck is done
    seasonguess.lost_driver_name = guesses[5]  # Pylance throws error but nullcheck is done
    db.session.commit()

    return redirect(f"/season/{user_name}")


@app.route("/result")
def result_root():
    return redirect("/result/Current")


@app.route("/result/<race_name>")
def result_active_race(race_name: str):
    model = TemplateModel()
    return render_template("enter.jinja",
                           active_result=model.race_result_by(race_name=race_name),
                           model=model)


@app.route("/result-enter/<result_race_name>", methods=["POST"])
def result_enter_post(result_race_name: str):
    pxxs: List[str] = request.form.getlist("pxxdrivers")
    dnfs: List[str] = request.form.getlist("dnf-drivers")
    excludes: List[str] = request.form.getlist("exclude-drivers")

    # Use strings as keys, as these dicts will be serialized to json
    pxxs_dict: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxxs)}
    dnfs_dict: Dict[str, str] = {str(position + 1): driver for position, driver in enumerate(pxxs) if driver in dnfs}

    raceresult: RaceResult | None = RaceResult.query.filter_by(race_name=result_race_name).first()

    if raceresult is None:
        raceresult = RaceResult()
        db.session.add(raceresult)

    raceresult.race_name = result_race_name
    raceresult.pxx_driver_names = pxxs_dict
    raceresult.dnf_driver_names = dnfs_dict if len(dnfs) > 0 else {"20": "NONE"}
    raceresult.excluded_driver_names = excludes
    db.session.commit()

    race: Race | None = Race.query.filter_by(name=result_race_name).first()
    if race is None:
        print("Error: Can't redirect to /enter/<GrandPrix> because race couldn't be found")
        return redirect(f"/result/Current")

    return redirect(f"/result/{race.name}")


@app.route("/user")
def user_root():
    users: List[User] = User.query.all()

    return render_template("users.jinja",
                           users=users)


@app.route("/user-add", methods=["POST"])
def user_add_post():
    username: str | None = request.form.get("select-add-user")

    if username is None or len(username) == 0:
        print(f"Not adding user, since no username was received")
        return user_root()

    if len(User.query.filter_by(name=username).all()) > 0:
        print(f"Not adding user {username}: Already exists!")
        return redirect("/user")

    user = User()
    user.name = username
    db.session.add(user)
    db.session.commit()

    return redirect("/user")


@app.route("/user-delete", methods=["POST"])
def user_delete_post():
    username = request.form.get("select-delete-user")

    if username is None or len(username) == 0:
        print(f"Not deleting user, since no username was received")
        return redirect("/user")

    if username == "Select User":
        return redirect("/user")

    print(f"Deleting user {username}...")

    User.query.filter_by(name=username).delete()
    db.session.commit()

    return redirect("/user")


if __name__ == "__main__":
    app.url_map.strict_slashes = False
    app.run(debug=True, host="0.0.0.0")
