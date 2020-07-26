from flask import jsonify, request, g, Blueprint, redirect
from app import db
from ..models import Solution
from app.auth import auth_token


solutions = Blueprint("solutions", __name__)


@solutions.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@solutions.route("/solutions", methods=["GET", "POST"])
def get_solutions():
    if request.method == "GET":
        if request.args:

            if "template_url" in request.args.keys():
                solution = Solution.query.filter_by(
                    template_url=request.args.get("template_url")
                ).first()
            elif "name" in request.args.keys():
                solution = Solution.query.filter_by(
                    name=request.args.get("name")
                ).first()
            else:
                return jsonify(
                    "The only columns searchable are 'name' and 'template_url",
                ), 404
            if solution:
                return solution
            else:
                return jsonify("solution not found"), 404
        else:
            return jsonify(
                [solution.export_data() for solution in Solution.query.all()]
            )
    elif request.method == "POST":
        solution = Solution()
        solution.check_import(request.json)
        db.session.add(solution)
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
