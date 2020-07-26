from flask import jsonify, request, g, Blueprint, redirect
from app import db
from ..models import VariableGroup
from app.auth import auth_token


var_groups = Blueprint("var_groups", __name__)


@solutions.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@solutions.route("/var_groups", methods=["GET", "POST"])
def get_var_groups():
    if request.method == "GET":
        return jsonify(
            [var_group.export_data() for var_group in VariableGroup.query.all()]
        )
    elif request.method == "POST":
        var_group = VariableGroup()
        var_group.check_import(request.json)
        db.session.add(var_group)
        db.session.commit()
        return jsonify({}), 201, {"Location": solution.get_url()}


@solutions.route("/solutions/<int:id>", methods=["GET", "DELETE"])
def get_solution(id):
    solution = Solution.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(
            solution.name, solution.template_url, solution.extra_vars, solutions.created
        )
    elif request.method == "DELETE":
        db.session.delete(solution)
        db.session.commit()
