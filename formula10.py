from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from model import *
from database_utils import reload_static_data, export_dynamic_data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db";
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;

db.init_app(app)


@app.route("/")
def index():
    users = User.query.all()
    raceresults = RaceResult.query.all()

    guesses = dict()
    for raceresult in raceresults:
        guesses[raceresult.race_id] = dict()
    for guess in Guess.query.all():
        guesses[guess.race_id][guess.user_id] = guess

    return render_template("index.jinja", users=users, raceresults=raceresults, guesses=guesses)


@app.route("/reload")
def reload():
    reload_static_data(db)
    return redirect("/")


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
