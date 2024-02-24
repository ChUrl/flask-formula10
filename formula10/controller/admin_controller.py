from typing import List
from urllib.parse import unquote
from flask import redirect, render_template, request
from werkzeug import Response

from formula10.database.update_query_util import update_race_result, update_user
from formula10.database.import_export_util import export_dynamic_data, reload_dynamic_data, reload_static_data
from formula10.frontend.template_model import TemplateModel
from formula10 import app


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