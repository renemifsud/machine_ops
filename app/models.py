import json, random
from app import db
import datetime
import jwt
from flask import url_for, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.errors.exceptions import ValidationError


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(2000), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    solved = db.Column(db.Boolean, index=True)
    name = db.Column(db.String(50), unique=True)
    solution_id = db.Column(db.Integer, db.ForeignKey("solutions.id"), index=True)
    __searchable__ = ["id", "data"]

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
        }

    def check_import(self, data, name=None, solution_id=None):
        try:
            self.user_id
            if type(data) is not str:
                self.data = json.dumps(data)
            else:
                self.data = data
            self.solved = False
            if name:
                self.name = name
            else:
                self.name = "alert_" + str(random.randint(100000, 99999999999))
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
    solutions = db.relationship("Solution", backref="creator", lazy="dynamic")
    var_groups = db.relationship("Var_Group", backref="creator", lazy="dynamic")
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
    playbook = db.Column(db.String(2000), unique=False)
    name = db.Column(db.String(200), unique=False)
    var_list = db.Column(db.String(1000), unique=False)
    var_groups = db.relationship("Var_Group", backref="tag", lazy="dynamic")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    alert = db.relationship("Alert", backref="alert", uselist=False)
    __searchable__ = ["id", "name", "playbook"]

    def get_url(self):
        return url_for("solution.get_solution", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.get_solution", id=self.id, _external=True)

    def export_data(self):
        return {"id": self.id, "name": self.name, "playbook": self.playbook}

    def check_import(self, name, playbook, var_list):
        try:
            self.playbook = playbook
            self.name = name
            self.var_list = json.dumps(var_list)
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
            raise ValidationError("Invalid 'Solution', missing " + e.args[0])
        return self


class Var_Group(db.Model):
    __tablename__ = "var_groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False)
    var_list = db.Column(db.String(500), unique=False)
    solution_id = db.Column(db.Integer, db.ForeignKey("solutions.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    __searchable__ = ["id", "name"]

    def get_url(self):
        return url_for("var_groups.get_var_group", id=self.id, _external=True)

    def get_app_url(self):
        return url_for("main.var_group", id=self.id, _external=True)

    def export_data(self):
        return {"id": self.id, "name": self.name, "var_list": json.loads(self.playbook)}

    def check_import(self, data):
        try:
            self.var_list = data["var_list"]
            self.name = data["name"]
        except KeyError as e:
            raise ValidationError("Invalid 'Variables Group', missing " + e.args[0])
        return self

    def check_import_app(self, name, var_list):
        try:
            self.var_list = json.dumps(var_list)
            self.name = name
        except KeyError as e:
            raise ValidationError("Invalid 'Variables Group', missing " + e.args[0])
        return self
