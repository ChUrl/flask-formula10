from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from model import *
from database_utils import reload_static_data, export_dynamic_data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route("/")
def index():
    return redirect("/race")


@app.route("/reload")
def reload():
    reload_static_data(db)
    return redirect("/")


@app.route("/save")
def save():
    export_dynamic_data()
    return redirect("/")


@app.route("/race")
def race():
    users = User.query.all()
    raceresults = RaceResult.query.all()
    drivers = Driver.query.all()

    guesses = dict()  # The guesses for which raceresults exist
    nextguesses = dict()  # The guesses that are still open for modification
    for raceresult in raceresults:
        guesses[raceresult.race_id] = dict()
    for guess in RaceGuess.query.all():
        if guess.race_id in guesses:
            guesses[guess.race_id][guess.user_id] = guess
        else:
            nextguesses[guess.user_id] = guess

    # TODO: Getting by ID might be stupid, get by date instead?
    nextid = raceresults[-1].race_id + 1 if len(raceresults) > 0 else 1
    nextrace = Race.query.filter_by(id=nextid).first()

    return render_template("race.jinja",
                           users=users,
                           drivers=drivers,
                           raceresults=raceresults,
                           guesses=guesses,
                           nextguesses=nextguesses,
                           nextrace=nextrace)


@app.route("/guessrace/<raceid>/<username>", methods=["POST"])
def guessrace(raceid, username):
    pxx = request.form.get("pxxselect")
    dnf = request.form.get("dnfselect")

    if pxx is None or dnf is None:
        return redirect("/race")

    raceguess: RaceGuess | None = RaceGuess.query.filter_by(user_id=username, race_id=raceid).first()

    if raceguess is not None:
        raceguess.pxx_id = pxx
        raceguess.dnf_id = dnf
    else:
        raceguess = RaceGuess()
        raceguess.user_id = username
        raceguess.race_id = raceid

        raceguess.pxx_id = pxx
        raceguess.dnf_id = dnf

        db.session.add(raceguess)

    db.session.commit()

    return redirect("/race")


@app.route("/enterresult")
def enterresult():
    return render_template("enterresult.jinja")


if __name__ == "__main__":
    app.run(debug=False)
