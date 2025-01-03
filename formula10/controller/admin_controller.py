from typing import List
from urllib.parse import unquote
from flask import redirect, render_template, request
from werkzeug import Response

from formula10.controller.error_controller import error_redirect
from formula10.database.update_queries import update_race_result, update_user
from formula10.domain.cache_invalidator import cache_invalidate_user_updated, cache_invalidate_race_result_updated
from formula10.domain.domain_model import Model
from formula10.domain.template_model import TemplateModel
from formula10 import app
from formula10.openf1.model.openf1_session import OpenF1Session
from formula10.openf1.openf1_definitions import OPENF1_SESSION_NAME_RACE
from formula10.openf1.openf1_fetcher import openf1_fetch_driver, openf1_fetch_position, openf1_fetch_session


@app.route("/result")
def result_root() -> Response:
    return redirect("/result/Current")


@app.route("/result/<race_name>")
def result_active_race(race_name: str) -> str:
    race_name = unquote(race_name)
    model = TemplateModel(active_user_name=None,
                          active_result_race_name=race_name)

    return render_template("result.jinja", model=model)


@app.route("/result-enter/<race_name>", methods=["POST"])
def result_enter_post(race_name: str) -> Response:
    race_name = unquote(race_name)
    pxxs: List[str] = request.form.getlist("pxx-drivers")
    first_dnfs: List[str] = request.form.getlist("first-dnf-drivers")
    dnfs: List[str] = request.form.getlist("dnf-drivers")
    excluded: List[str] = request.form.getlist("excluded-drivers")

    # Extra stats for points calculation
    fastest_lap: str | None = request.form.get("fastest-lap")
    sprint_pxxs: List[str] = request.form.getlist("sprint-pxx-drivers")
    sprint_dnf_drivers: List[str] = request.form.getlist("sprint-dnf-drivers")

    if fastest_lap is None:
        return error_redirect("Data was not saved, because fastest lap was not set.")

    cache_invalidate_race_result_updated()
    race_id: int = Model().race_by(race_name=race_name).id
    return update_race_result(race_id, pxxs, first_dnfs, dnfs, excluded, int(fastest_lap), sprint_pxxs, sprint_dnf_drivers)


@app.route("/result-fetch/<race_name>", methods=["POST"])
def result_fetch_post(race_name: str) -> Response:
    session: OpenF1Session = openf1_fetch_session(OPENF1_SESSION_NAME_RACE, "KSA")
    openf1_fetch_driver(session.session_key, "VER")
    openf1_fetch_position(session.session_key, 1)

    # @todo Fetch stuff and build the race_result using update_race_result(...)

    cache_invalidate_race_result_updated()
    return redirect("/result")


@app.route("/user")
def user_root() -> str:
    model = TemplateModel(active_user_name=None,
                          active_result_race_name=None)

    return render_template("users.jinja", model=model)


@app.route("/user-add", methods=["POST"])
def user_add_post() -> Response:
    cache_invalidate_user_updated()
    username: str | None = request.form.get("select-add-user")
    return update_user(username, add=True)


@app.route("/user-delete", methods=["POST"])
def user_delete_post() -> Response:
    cache_invalidate_user_updated()
    username: str | None = request.form.get("select-delete-user")
    return update_user(username, delete=True)
