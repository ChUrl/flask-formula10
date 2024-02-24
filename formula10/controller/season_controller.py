from typing import List
from urllib.parse import unquote
from flask import redirect, render_template, request
from werkzeug import Response

from formula10.database.model.team import Team
from formula10.database.update_query_util import update_season_guess
from formula10.frontend.template_model import TemplateModel
from formula10 import app, db


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
    # TODO: This is pretty ugly, to do queries in the controller
    team_winner_guesses: List[str | None] = [
        request.form.get(f"teamwinner-{team.name}") for team in db.session.query(Team).all()
    ]
    podium_driver_guesses: List[str] = request.form.getlist("podiumdrivers")

    return update_season_guess(user_name, guesses, team_winner_guesses, podium_driver_guesses)