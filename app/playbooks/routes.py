from flask import jsonify, request, g, Blueprint, redirect
from app import db
from ..models import Playbook
from app.auth import auth_token


playbooks = Blueprint("playbooks", __name__)


@playbooks.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


@playbooks.route("/playbooks", methods=["GET", "POST"])
def get_playbooks():
    if request.method == "GET":
        if request.args:
            if "template_url" in request.args.keys():
                playbook = Playbook.query.filter_by(
                    template_url=request.args.get("template_url")
                ).first()
            elif "name" in request.args.keys():
                playbook = Playbook.query.filter_by(
                    name=request.args.get("name")
                ).first()
            else:
                return (
                    jsonify(
                        "The only columns searchable are 'name' and 'template_url",
                    ),
                    404,
                )
            if playbook:
                return playbook
            else:
                return jsonify("playbook not found"), 404
        else:
            return jsonify(
                [playbook.export_data() for playbook in Playbook.query.all()]
            )
    elif request.method == "POST":
        playbook = Playbook()
        playbook.check_import(request.json)
        db.session.add(playbook)
        db.session.commit()
        return jsonify({}), 201, {"Location": playbook.get_url()}


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
