from flask import jsonify, request, g, Blueprint
from app import db
from ..models import Alert
from app.auth import auth_token

alerts = Blueprint("alerts", __name__)


@alerts.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@alerts.route("/alerts/", methods=["GET"])
def get_alerts():
    return jsonify({"alerts": [alert.get_url() for alert in Alert.query.all()]})


@alerts.route("/alerts/<int:id>", methods=["GET", "DELETE"])
def get_alert(id):
    alert = Alert.query.get_or_404(id).export_data()
    if request.method == "GET":
        return jsonify(alert)
    elif request.method == "DELETE":
        db.session.delete(alert)
        db.session.commit()


@alerts.route("/alerts", methods=["POST"])
def new_alert():
    alert = Alert(creator=g.user)
    alert.check_import(request.json)
    db.session.add(alert)
    db.session.commit()
    return jsonify({}), 201, {"Location": alert.get_url()}
