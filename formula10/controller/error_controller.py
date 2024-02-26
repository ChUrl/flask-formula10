from typing import cast
from flask import redirect, render_template, session
from werkzeug import Response

from formula10.frontend.template_model import TemplateModel
from formula10 import app

def error_redirect(error_message: str) -> Response:
    session["error_message"] = error_message
    return redirect(f"/error")

@app.route("/error")
def error_root() -> str:
    model = TemplateModel(active_user_name=None, active_result_race_name=None)
    message: str = cast(str, session["error_message"])

    return render_template("error.jinja", model=model, error_message=message)
