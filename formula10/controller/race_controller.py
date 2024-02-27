from urllib.parse import unquote
from flask import redirect, render_template, request
from werkzeug import Response

from formula10.database.update_queries import delete_race_guess, update_race_guess
from formula10.domain.template_model import TemplateModel
from formula10 import app


@app.route("/")
def root() -> Response:
    return redirect("/race/Everyone")


@app.route("/race")
def race_root() -> Response:
    return redirect("/race/Everyone")


@app.route("/race/<user_name>")
def race_active_user(user_name: str) -> str:
    user_name = unquote(user_name)
    model = TemplateModel(active_user_name=user_name,
                          active_result_race_name=None)

    return render_template("race.jinja", model=model)


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