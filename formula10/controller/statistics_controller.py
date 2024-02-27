from flask import render_template
from formula10 import app
from formula10.domain.template_model import TemplateModel

@app.route("/graphs")
def graphs_root() -> str:
    model = TemplateModel(active_user_name=None, active_result_race_name=None)

    return render_template("statistics.jinja", model=model)