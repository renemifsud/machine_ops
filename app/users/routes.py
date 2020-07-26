from flask import jsonify, request, Blueprint, current_app
from app import db
from app.models import User
from app.auth import auth_token

users = Blueprint("users", __name__)


@users.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@users.route("/users/", methods=["GET"])
def get_users():
    return jsonify({"users": [user.get_url() for user in User.query.all()]})


@users.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    return jsonify(User.query.get_or_404(id).export_data())


@users.route("/users", methods=["POST"])
def new_user():
    user = User()
    user.check_import(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify({}), 201, {"Location": user.get_url()}


@users.route("/users/<int:id>", methods=["PUT"])
def edit_user(id):
    user = User.query.get_or_404(id)
    user.import_data(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify({})
