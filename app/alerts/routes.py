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

@alerts.route('/alerts/', methods=['GET'])
def get_alerts():
    return jsonify({'alerts': [alert.get_url() for alert in
                                  Alert.query.all()]})


@alerts.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    return jsonify(Alert.query.get_or_404(id).export_data())


@alerts.route('/alerts', methods=['POST'])
def new_alert():
    alert = Alert(creator=g.user)
    alert.check_import(request.json)
    db.session.add(alert)
    db.session.commit()
    return jsonify({}), 201, {'Location': alert.get_url()}


@alerts.route('/alerts/<int:id>', methods=['PUT'])
def edit_alert(id):
    alert = Alert.query.get_or_404(id)
    alert.import_data(request.json)
    db.session.add(alert)
    db.session.commit()
    return jsonify({})
