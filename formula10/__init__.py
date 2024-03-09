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
import formula10.controller.leaderboard_controller
import formula10.controller.statistics_controller
import formula10.controller.rules_controller
import formula10.controller.admin_controller
import formula10.controller.error_controller