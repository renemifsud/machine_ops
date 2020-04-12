from flask import jsonify, request, g
from . import api
from .. import db
from ..models import Alert


@api.route('/alerts/', methods=['GET'])
def get_alerts():
    return jsonify({'alerts': [alert.get_url() for alert in
                                  Alert.query.all()]})


@api.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    return jsonify(Alert.query.get_or_404(id).export_data())


@api.route('/alerts', methods=['POST'])
def new_alert():
    alert = Alert(creator=g.user)
    alert.check_import(request.json)
    db.session.add(alert)
    db.session.commit()
    return jsonify({}), 201, {'Location': alert.get_url()}


@api.route('/alerts/<int:id>', methods=['PUT'])
def edit_alert(id):
    alert = Alert.query.get_or_404(id)
    alert.import_data(request.json)
    db.session.add(alert)
    db.session.commit()
    return jsonify({})
