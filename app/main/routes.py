from flask import Blueprint, render_template, session, current_app, g, make_response
from app.models import User

main = Blueprint("main", __name__)


@main.before_request
def before_request():
    if current_app.config.get("IGNORE_AUTH") is True:
        g.user = User.query.get(1)
    else:
        g.user = User.verify_auth_token(session.get("token"))
        if g.user is not None:
            pass
        else:
            return "Unauthorised"


@main.route("/home", methods=["GET"])
def testb():
    return render_template("home.html")
