from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from model import *
from database_utils import reload_static_data, export_dynamic_data

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///formula10.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def index():
    reload_static_data(db)

    return render_template("index.jinja")


@app.route("/seasons/")
def default_season():
    return redirect("/seasons/2023/p10")


@app.route("/seasons/<year>/")
def default_statistic(year):
    return redirect("/seasons/" + year + "/p10")


@app.route("/seasons/<year>/<statistic>/")
def seasons(year, statistic):
    seasons = Season.query.all()

    return render_template(
        "season.jinja", year=year, statistic=statistic, seasons=seasons
    )


# @app.route("/teams", methods=["GET", "POST"])
# def teams():
#     if request.method == "POST":
#         new_team = Team(
#             name = request.form["name"],
#             country_code = request.form["country_code"]
#         )
#         print(new_team.name, new_team.country_code)
#         db.session.add(new_team)
#         db.session.commit()
#
#     return render_template("teams.jinja", page="teams")


if __name__ == "__main__":
    app.run(debug=False)
