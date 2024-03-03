import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load local ENV variables (can be set when calling the executable)
ENABLE_TIMING: bool = False if os.getenv("DISABLE_TIMING") == "True" else True
ENABLE_DEBUG_ENDPOINTS: bool = True if os.getenv("ENABLE_DEBUG_ENDPOINTS") == "True" else False
print("Running Formula10 with:")
if not ENABLE_TIMING:
    print("- Disabled timing constraints")
if ENABLE_DEBUG_ENDPOINTS:
    print("- Enabled debug endpoints")

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
import formula10.controller.leaderboard_controller
import formula10.controller.statistics_controller
import formula10.controller.rules_controller
import formula10.controller.admin_controller
import formula10.controller.error_controller


# TODO
# Leaderboard

# - For season guess calc there is missing: Fastest laps + sprint points + sprint DNFs (in race result)

# - Auto calculate season points (display season points?)
# - Interesting stats:
#   - Which driver was voted most for dnf (top 5)?

# General
# - Decouple names from IDs + Fix Valtteri/Russel spelling errors
# - Unit testing (as much as possible, but especially points calculation)
# - Add links to the official F1 stats page (for quali/result), probably best to store entire link in DB (because they are not entirely regular)?