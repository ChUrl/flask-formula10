from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///formula10.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.url_map.strict_slashes = False

db: SQLAlchemy = SQLAlchemy()
db.init_app(app)

# NOTE: These imports are required to register the routes. They need to be after "app" is declared
import formula10.controller.race_controller  # type: ignore
import formula10.controller.season_controller  # type: ignore
import formula10.controller.admin_controller  # type: ignore


# TODO
# General

# Split the database model from the frontend-model/template-model/domain-model
# - Move most of the template logic into this
# - Allow exclusion of e.g. most-gained driver and other stuff

# - Choose "place to guess" late before the race? Make a page for this
# - Rules page

# - Make user order changeable using drag'n'drop?
# - Show place when entering race result (would require updating the drag'n'drop code...)
# - Show cards of previous race results, like with season guesses?
# - Make the season card grid left-aligned? So e.g. 2 cards are not spread over the whole screen with large gaps?

# Statistics
# - Auto calculate points
# - Order user table by points + display points somewhere
# - Show current values for some season guesses (e.g. current most dnfs)
# - Generate static diagram using chart.js + templating the js (funny yikes)


# if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0")