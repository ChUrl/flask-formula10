from typing import List
from urllib.parse import unquote
from flask import redirect, render_template, request
from werkzeug import Response

from formula10.database.model.db_team import DbTeam
from formula10.database.update_queries import update_season_guess
from formula10.domain.model.team import NONE_TEAM
from formula10.domain.points_model import PointsModel
from formula10.domain.template_model import TemplateModel
from formula10 import app, db


@app.route("/season")
def season_root() -> Response:
    return redirect("/season/Everyone")


@app.route("/season/<user_name>")
def season_active_user(user_name: str) -> str:
    user_name = unquote(user_name)
    model = TemplateModel(active_user_name=user_name,
                          active_result_race_name=None)
    points = PointsModel()

    return render_template("season.jinja", model=model, points=points)


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
        request.form.get(f"teamwinner-{team.name}") for team in db.session.query(DbTeam).all() if team.name != NONE_TEAM.name
    ]
    podium_driver_guesses: List[str] = request.form.getlist("podiumdrivers")

    return update_season_guess(user_name, guesses, team_winner_guesses, podium_driver_guesses)