from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session cookie is used to propagate message to error page
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'ich stinke nach maggi'

app.url_map.strict_slashes = False

db: SQLAlchemy = SQLAlchemy()
db.init_app(app)

# NOTE: These imports are required to register the routes. They need to be imported after "app" is declared
import formula10.controller.race_controller  # type: ignore
import formula10.controller.season_controller
import formula10.controller.statistics_controller
import formula10.controller.rules_controller
import formula10.controller.admin_controller
import formula10.controller.error_controller


# TODO
# General

# Create a model baseclass that contains the cached teams/drivers/races etc., so the points + template model can be derived from it

# Statistics
# - Auto calculate points
# - Display points somewhere in race table? Below the name in the table header.
# - Highlight currently correct values for some season guesses (e.g. current most dnfs, team winners, podiums)
# - Generate static diagram using chart.js + templating the js (funny yikes)
# - Which driver was voted most for dnf?

# Possible but probably not
# - Show cards of previous race results, like with season guesses?
# - Make user order changeable using drag'n'drop?