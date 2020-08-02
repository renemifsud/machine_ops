import json, random
from app import db, datasets_dir
import datetime
import jwt
from flask import url_for, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.errors.exceptions import ValidationError
from sqlalchemy_utc import UtcDateTime, utcnow
import dateutil.parser


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(5000), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    solved = db.Column(db.Boolean, index=True)
    name = db.Column(db.String(50), unique=True)
    solution_id = db.Column(db.Integer, db.ForeignKey("solutions.id"), index=True)
    __searchable__ = ["id", "data", "name"]

    def get_url(self):
        return url_for("alerts.get_alert", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.alert", id=self.id, _external=True)

    def export_data(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "data": self.data,
            "solved": self.solved,
            "solution_id": self.solution_id,
            "name": self.name,
            "location": self.get_app_url(),
        }

    def check_import(self, data, name=None, solution_id=None, solved=False):
        try:
            self.user_id
            if type(data) is not str:
                self.data = json.dumps(data)
            else:
                self.data = data
            if name:
                self.name = name
            else:
                self.name = "alert_" + str(random.randint(100000, 99999999999))
            if solution_id:
                self.solution_id = solution_id

            self.solved = solved
        except KeyError as err:
            raise ValidationError("The alert is not JSON Serialisable")
        return self


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False)
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(30), index=True, unique=True)
    alerts = db.relationship("Alert", backref="creator", lazy="dynamic")
    var_groups = db.relationship("VariableGroup", backref="creator", lazy="dynamic")
    solutions = db.relationship("Solution", backref="creator", lazy="dynamic")
    __searchable__ = ["id", "username", "email"]

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_url(self):
        return url_for("users.get_user", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.get_user", id=self.id, _external=True)

    def export_data(self):
        return {"self_url": self.get_url(), "username": self.username}

    def check_import(self, data):
        try:
            self.username = data["username"]
            self.email = data["email"]
            self.set_password(data["password"])
        except KeyError as e:
            raise ValidationError("Invalid 'User', missing " + e.args[0])
        return self

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"])
        except:
            return None
        return User.query.get(data["id"])

    def generate_auth_token(self, expires_in=3600):
        token = jwt.encode(
            {
                "id": self.id,
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(seconds=expires_in),
            },
            current_app.config["SECRET_KEY"],
        ).decode("UTF-8")
        return token


class Solution(db.Model):
    __tablename__ = "solutions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    playbook_id = db.Column(db.Integer, db.ForeignKey("playbooks.id"), index=True)
    var_group_id = db.Column(
        db.Integer, db.ForeignKey("variable_groups.id"), index=True
    )
    created = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    modified = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    last_job_run = db.Column(UtcDateTime(), nullable=False, default=utcnow())

    alerts = db.relationship("Alert", backref="solution", uselist=False)
    __searchable__ = ["id", "name"]

    def get_url(self):
        return url_for("solutions.get_solution", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.get_solution", id=self.id, _external=True)

    def export_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
        }

    def check_import(self, obj):
        try:
            self.name = obj["name"]

            if obj["last_job_run"]:
                self.last_job_run = dateutil.parser.parse(obj["last_job_run"])
            else:
                self.last_job_run = None
            if obj["created"]:
                self.created = dateutil.parser.parse(obj["created"])
            else:
                self.created = None
            if obj["modified"]:
                self.modified = dateutil.parser.parse(obj["modified"])
            else:
                self.modified = None

        except KeyError as e:
            raise ValidationError("Invalid 'Solution', missing " + e.args[0])
        return self

    def check_import_app(self, name, playbook_id, var_group_id):
        try:
            self.playbook_id = playbook_id
            self.var_group_id = var_group_id
            self.name = name
        except KeyError as e:
            raise ValidationError("Invalid 'Solution', missing " + e.args[0])
        return self


class Playbook(db.Model):
    __tablename__ = "playbooks"
    id = db.Column(db.Integer, primary_key=True)
    template_url = db.Column(db.String(200), nullable=False, unique=True, index=True)
    job_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    name = db.Column(db.String(200), unique=False)
    extra_vars = db.Column(db.String(200), unique=False)
    created = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    modified = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    last_job_run = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    verbosity_level = db.Column(db.Integer, unique=False)
    created_by = db.Column(db.String(200), unique=False)
    credential_name = db.Column(db.String(200), unique=False)
    inventory_name = db.Column(db.String(200), unique=False)

    solution = db.relationship("Solution", backref="playbook", uselist=False)
    __searchable__ = ["id", "name", "template_url", "job_id"]

    def get_url(self):
        return url_for("playbooks.get_playbook", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.get_playbook", id=self.id, _external=True)

    def export_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "template_url": self.template_url,
            "created": self.created,
        }

    def check_import(self, obj):
        try:
            self.name = obj["name"]
            self.extra_vars = obj["extra_vars"]

            if obj["last_job_run"]:
                self.last_job_run = dateutil.parser.parse(obj["last_job_run"])
            else:
                self.last_job_run = None
            if obj["created"]:
                self.created = dateutil.parser.parse(obj["created"])
            else:
                self.created = None
            if obj["modified"]:
                self.modified = dateutil.parser.parse(obj["modified"])
            else:
                self.modified = None

            self.template_url = obj["url"]
            self.job_id = self.template_url.replace("/api/v2/job_templates/", "")[:-1]
            self.verbosity_level = obj["verbosity"]
            self.created_by = obj["summary_fields"]["created_by"]["username"]
            self.inventory = obj["summary_fields"]["inventory"]["name"]
        except KeyError as e:
            raise ValidationError("Invalid 'Solution', missing " + e.args[0])
        return self

    def check_import_app(self, name, playbook, var_list):
        try:
            self.playbook = playbook
            self.name = name
            var_list = [
                "".join(e for e in var if e.isalnum())
                for var in var_list.split(""",""")
            ]
            self.var_list = json.dumps(var_list)
        except KeyError as e:
            raise ValidationError("Invalid 'Playbook', missing " + e.args[0])
        return self


class VariableGroup(db.Model):
    __tablename__ = "variable_groups"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    name = db.Column(db.String(200), unique=False)
    variables = db.Column(db.String(200), unique=False)
    created = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    modified = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    __searchable__ = ["id", "name"]

    def get_url(self):
        return url_for("var_groups.get_var_groups", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.var_group", id=self.id, _external=True)

    def export_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "created": self.created,
        }

    def check_import(self, obj):
        try:
            self.name = obj["name"]

            if obj["created"]:
                self.created = dateutil.parser.parse(obj["created"])
            else:
                self.created = None
            if obj["modified"]:
                self.modified = dateutil.parser.parse(obj["modified"])
            else:
                self.modified = None

        except KeyError as e:
            raise ValidationError("Invalid 'Solution', missing " + e.args[0])
        return self

    def check_import_app(self, name, variables):
        try:
            self.name = name
            self.variables = json.dumps(variables)
        except KeyError as e:
            raise ValidationError("Invalid 'Playbook', missing " + e.args[0])
        return self


class MlModels(db.Model):
    __tablename__ = "ml_models"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithms.id"), index=True)
    data = db.Column(db.LargeBinary)
    created = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    __searchable__ = ["id"]

    def get_url(self):
        return url_for("ml_models.get_ml_models", id=self.id, _external=True)

    def export_data(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created": self.created,
        }

    def check_import(self, data):
        try:
            self.data = data
        except KeyError as e:
            raise ValidationError("Invalid 'Playbook', missing " + e.args[0])
        return self


class Algorithms(db.Model):
    __tablename__ = "algorithms"
    id = db.Column(db.Integer, primary_key=True)
    config = db.Column(db.String(200), unique=False)
    type_id = db.Column(db.Integer, db.ForeignKey("algorithms_types.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    created = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    ml_models = db.relationship("MlModels", backref="algorithm", uselist=False)

    __searchable__ = ["id"]

    def get_url(self):
        return url_for("ml_models.get_ml_models", id=self.id, _external=True)

    def export_data(self):
        return {
            "id": self.id,
            "config": self.config,
            "created": self.created,
        }

    def check_import_app(self, config: dict):
        try:
            self.config = json.dumps(config)
        except KeyError as e:
            raise ValidationError("Invalid 'Playbook', missing " + e.args[0])
        return self


class AlgorithmsTypes(db.Model):
    __tablename__ = "algorithms_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    params = db.Column(db.String(200), unique=False)
    created = db.Column(UtcDateTime(), nullable=False, default=utcnow())
    algorithms = db.relationship("Algorithms", backref="type", uselist=False)
    __searchable__ = ["id"]

    def get_url(self):
        return url_for("ml_models.get_ml_models", id=self.id, _external=True)

    def set_params(self, *args):
        self.params = json.dumps(args)

    def export_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "params": self.params,
            "created": self.created,
        }

    def check_import_app(self, name, config):
        try:
            self.name = name
        except KeyError as e:
            raise ValidationError("Invalid 'Playbook', missing " + e.args[0])
        return self
