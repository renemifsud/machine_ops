from flask import jsonify, request, g, Blueprint
from app import db
from ..models import Alert
from app.auth import auth_token
import json

alerts = Blueprint("alerts", __name__)


@alerts.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@alerts.route("/alerts/", methods=["GET", "POST"])
def get_alerts():
    if request.method == "GET":
        return jsonify([alert.export_data() for alert in Alert.query.all()])
    if request.method == "POST":
        alert = Alert(creator=g.user)
        alert.check_import(request.json)
        db.session.add(alert)
        db.session.commit()
        return jsonify({}), 201, {"Location": alert.get_url()}


@alerts.route("/alerts/bulk_search", methods=["POST"])
def bulk_search():
    if request.method == "POST":
        query = request.form["query"]
        query = "%{}%".format(query)
        return (
            jsonify(
                [
                    alert.export_data()
                    for alert in Alert.query.filter(Alert.data.like(query)).all()
                ]
            ),
            200,
        )


@alerts.route("/alerts/<int:id>", methods=["GET", "DELETE"])
def get_alert(id):
    alert = Alert.query.get_or_404(id).export_data()
    if request.method == "GET":
        return jsonify(alert)
    elif request.method == "DELETE":
        db.session.delete(alert)
        db.session.commit()


@alerts.route("/alerts/bulk_set_solution", methods=["POST"])
def alert_set_bulk_solution():
    for alert_id in json.loads(request.form["alerts"]):
        Alert.query.filter_by(id=alert_id).update(
            {"solution_id": request.form["solution_id"]}
        )
        db.session.commit()
    return jsonify("Alerts updated"), 204
