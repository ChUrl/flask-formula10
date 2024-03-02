import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load local ENV variables (can be set when calling the executable)
ENABLE_TIMING: bool = False if os.getenv("DISABLE_TIMING") == "True" else True
print("Running Formula10 with:")
if not ENABLE_TIMING:
    print("- Disabled timing constraints")

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
# Statistics
# - Display total points somewhere in race table? Below the name in the table header.
# - Auto calculate season points
# - Highlight currently correct values for some season guesses (e.g. current most dnfs, team winners, podiums)
# - Generate static diagram using chart.js + templating the js (funny yikes)
# - Interesting stats:
#   - Which driver was voted most for dnf (top 5)?

# General
# - Decouple names from IDs + Fix Valtteri/Russel spelling errors
# - Unit testing (as much as possible, but especially points calculation)
# - Add links to the official F1 stats page (for quali/result), probably best to store entire link in DB (because they are not entirely regular)?

# Possible but probably not
# - Show cards of previous race results, like with season guesses?
# - Make user order changeable using drag'n'drop?