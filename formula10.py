from typing import List
from urllib.parse import unquote
from flask import Flask, render_template, request, redirect
from werkzeug import Response
from model import Team, db
from file_utils import reload_static_data, reload_dynamic_data, export_dynamic_data
from template_model import TemplateModel
from backend_model import delete_race_guess, update_race_guess, update_race_result, update_season_guess, update_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.url_map.strict_slashes = False

db.init_app(app)


# TODO
# General

# - Choose "place to guess" late before the race? Make a page for this
# - Make user order changeable using drag'n'drop?

# - Show place when entering race result (would require updating the drag'n'drop code...)
# - Show cards of previous race results, like with season guesses?
# - Make the season card grid left-aligned? So e.g. 2 cards are not spread over the whole screen with large gaps?

# Statistics
# - Auto calculate points
# - Order user table by points + display points somewhere
# - Show current values for some season guesses (e.g. current most dnfs)
# - Generate static diagram using chart.js + templating the js (funny yikes)

# Rules page


@app.route("/")
def root() -> Response:
    return redirect("/race/Everyone")


@app.route("/save/all")
def save() -> Response:
    export_dynamic_data()
    return redirect("/")


@app.route("/load/all")
def load() -> Response:
    reload_static_data()
    reload_dynamic_data()
    return redirect("/")


@app.route("/load/static")
def load_static() -> Response:
    reload_static_data()
    return redirect("/")


@app.route("/load/dynamic")
def load_dynamic() -> Response:
    reload_dynamic_data()
    return redirect("/")


@app.route("/race")
def race_root() -> Response:
    return redirect("/race/Everyone")


@app.route("/race/<user_name>")
def race_active_user(user_name: str) -> str:
    user_name = unquote(user_name)
    model = TemplateModel()
    return render_template("race.jinja",
                           active_user=model.user_by(user_name=user_name, ignore=["Everyone"]),
                           model=model)


@app.route("/race-guess/<race_name>/<user_name>", methods=["POST"])
def race_guess_post(race_name: str, user_name: str) -> Response:
    race_name = unquote(race_name)
    user_name = unquote(user_name)

    pxx: str | None = request.form.get("pxxselect")
    dnf: str | None = request.form.get("dnfselect")

    return update_race_guess(race_name, user_name, pxx, dnf)


@app.route("/race-guess-delete/<race_name>/<user_name>", methods=["POST"])
def race_guess_delete_post(race_name: str, user_name: str) -> Response:
    race_name = unquote(race_name)
    user_name = unquote(user_name)

    return delete_race_guess(race_name, user_name)


@app.route("/season")
def season_root() -> Response:
    return redirect("/season/Everyone")


@app.route("/season/<user_name>")
def season_active_user(user_name: str) -> str:
    user_name = unquote(user_name)
    model = TemplateModel()
    return render_template("season.jinja",
                           active_user=model.user_by(user_name=user_name, ignore=["Everyone"]),
                           model=model)


@app.route("/season-guess/<user_name>", methods=["POST"])
def season_guess_post(user_name: str) -> Response:
    user_name = unquote(user_name)
    guesses: List[str | None] = [
        request.form.get("hottakeselect"),
        request.form.get("p2select"),
        request.form.get("overtakeselect"),
        request.form.get("dnfselect"),
        request.form.get("gainedselect"),
        request.form.get("lostselect")
    ]
    team_winner_guesses: List[str | None] = [
        request.form.get(f"teamwinner-{team.name}") for team in db.session.query(Team).all()
    ]
    podium_driver_guesses: List[str] = request.form.getlist("podiumdrivers")

    return update_season_guess(user_name, guesses, team_winner_guesses, podium_driver_guesses)


@app.route("/result")
def result_root() -> Response:
    return redirect("/result/Current")


@app.route("/result/<race_name>")
def result_active_race(race_name: str) -> str:
    race_name = unquote(race_name)
    model = TemplateModel()
    return render_template("enter.jinja",
                           active_result=model.race_result_by(race_name=race_name),
                           model=model)


@app.route("/result-enter/<race_name>", methods=["POST"])
def result_enter_post(race_name: str) -> Response:
    race_name = unquote(race_name)
    pxxs: List[str] = request.form.getlist("pxx-drivers")
    first_dnfs: List[str] = request.form.getlist("first-dnf-drivers")
    dnfs: List[str] = request.form.getlist("dnf-drivers")
    excluded: List[str] = request.form.getlist("excluded-drivers")

    return update_race_result(race_name, pxxs, first_dnfs, dnfs, excluded)


@app.route("/user")
def user_root() -> str:
    model = TemplateModel()
    return render_template("users.jinja",
                           model=model)


@app.route("/user-add", methods=["POST"])
def user_add_post() -> Response:
    username: str | None = request.form.get("select-add-user")
    return update_user(username, add=True)


@app.route("/user-delete", methods=["POST"])
def user_delete_post() -> Response:
    username: str | None = request.form.get("select-delete-user")
    return update_user(username, delete=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
