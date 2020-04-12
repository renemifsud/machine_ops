from flask import jsonify, request
from . import api
from .. import db
from ..models import User


@api.route('/users/', methods=['GET'])
def get_users():
    return jsonify({'users': [user.get_url() for user in
                                  User.query.all()]})


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).export_data())


@api.route('/users', methods=['POST'])
def new_user():
    user = User()
    user.check_import(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify({}), 201, {'Location': user.get_url()}


@api.route('/users/<int:id>', methods=['PUT'])
def edit_user(id):
    user = User.query.get_or_404(id)
    user.import_data(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify({})
