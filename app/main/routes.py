from flask import (
    Blueprint,
    render_template,
    session,
    current_app,
    g,
    make_response,
    redirect,
)
from app.models import User, Alert

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
            return redirect("/login")


@main.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@main.route("/alerts/<int:id>", methods=["GET"])
def alert(id):
    alert = Alert.query.get_or_404(id)
    if alert:
        return render_template("alert.html", alert=alert)


@main.route("/alerts", methods=["GET"])
def list_alerts():
    alerts = Alert.query.all()
    return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/solved", methods=["GET"])
def solved():
    alerts = Alert.query.filter_by(solved=True).all()
    if alert:
        return render_template("list_alerts.html", alerts=alerts, selected="alerts")


@main.route("/alerts/triggering", methods=["GET"])
def triggering():
    alerts = Alert.query.filter_by(solved=False).all()
    return render_template("list_alerts.html", alerts=alerts, selected="alerts")
