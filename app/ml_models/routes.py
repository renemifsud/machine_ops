from flask import jsonify, request, g, Blueprint, redirect
from app import db
from ..models import MlModels, Algorithms, AlgorithmsTypes
from app.auth import auth_token
import fasttext


ml_models = Blueprint("ml_models", __name__)


@ml_models.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@ml_models.route("/ml_models", methods=["GET", "POST"])
def get_ml_model():
    if request.method == "GET":
        return jsonify([ml_model.export_data() for ml_model in MlModels.query.all()])
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


@playbooks.route("/playbooks/<int:id>", methods=["GET", "DELETE"])
def get_playbook(id):
    playbook = Playbook.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(
            {
                "name": playbook.name,
                "url": playbook.template_url,
                "extra_vars": playbook.extra_vars,
                "created": playbook.created,
            }
        )
    elif request.method == "DELETE":
        db.session.delete(playbook)
        db.session.commit()
