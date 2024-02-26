from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.url_map.strict_slashes = False

db: SQLAlchemy = SQLAlchemy()
db.init_app(app)

# NOTE: These imports are required to register the routes. They need to be imported after "app" is declared
import formula10.controller.race_controller  # type: ignore
import formula10.controller.season_controller  # type: ignore
import formula10.controller.admin_controller  # type: ignore


# TODO
# General

# - Show date for race name, also store time in database
# - Choose "place to guess" late before the race? Make a page for this?
# - Rules page

# - Make user order changeable using drag'n'drop?
# - Show place when entering race result (would require updating the drag'n'drop code...)
# - Show cards of previous race results, like with season guesses?

# Statistics
# - Rename "Statistics" to "Leaderboard"
# - Auto calculate points
# - Order user table by points + display points somewhere
# - Highlight currently correct values for some season guesses (e.g. current most dnfs)
# - Generate static diagram using chart.js + templating the js (funny yikes)