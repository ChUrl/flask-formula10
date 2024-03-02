from flask import render_template
from formula10 import app
from formula10.domain.points_model import PointsModel
from formula10.domain.template_model import TemplateModel

@app.route("/graphs")
def graphs_root() -> str:
    model = TemplateModel(active_user_name=None, active_result_race_name=None)
    points = PointsModel()

    return render_template("leaderboard.jinja", model=model, points=points)