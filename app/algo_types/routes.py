from flask import jsonify, request, g, Blueprint, redirect
from app import db
from ..models import AlgorithmsTypes
from app.auth import auth_token
import fasttext


algo_types = Blueprint("algo_types", __name__)


@algo_types.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@algo_types.route("/algo_types", methods=["GET", "POST"])
def get_algo_types():
    if request.method == "GET":
        return jsonify(
            [algo_types.export_data() for algo_types in AlgorithmsTypes.query.all()]
        )
    elif request.method == "POST":
        # Creating Algorithm
        algo = Algorithms(creator=g.user, type=request.form["algorithm_type_id"])
        algo.check_import_app(request.get("config"))
        db.session.add(algo)
        db.session.commit()

        # Getting solutions
        solutions = Solutions.query.all()

        dataset = {}
        for solution in solutions:
            alerts = [
                {solution_id: alert.data}
                for alert in Alerts.query.filter_by(solution_id=solution.id)
            ]
            dataset[solution_id] = alerts

        # data_model = fasttext.train_supervised(
        #     input="cooking.train",
        #     lr=request.form["lr"],
        #     epoch=request.form["epoch"],
        #     wordNgrams=request.form["wordNgrams"],
        # )

        # ml_model = MlModels(creator=g.user, algorithm=algo.id)
        # ml_model.check_import_app
        # playbook.check_import()
        # db.session.add(playbook)
        # db.session.commit()
        return jsonify({}), 201, "done"

@algo_types.route("/algo_types/<int:id>", methods=["GET", "POST"])
def get_algo_type(id):
    algo_type = AlgorithmsTypes.query.get_or_404(id)
    return jsonify(algo_type.export_data()), 200