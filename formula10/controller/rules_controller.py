from flask import render_template

from formula10 import app
from formula10.frontend.template_model import TemplateModel

@app.route("/rules")
def rules_root() -> str:
    model = TemplateModel(active_user_name=None, active_result_race_name=None)

    return render_template("rules.jinja", model=model)