import json
from app import db
import datetime
import jwt
from flask import url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.errors.exceptions import ValidationError


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    def get_url(self):
        return url_for("alerts.get_alert", id=self.id, _external=True)

    def export_data(self):
        return {"id": self.id, "user_id": self.user_id, "data": json.loads(self.data)}

    def check_import(self, data):
        try:
            self.user_id
            self.data = json.dumps(data)
        except KeyError as err:
            raise ValidationError("The alert is not JSON Serialisable")
        return self


class User(db.Model):
    __tablename__ = "users"
    exclude_attrs = ["password_hash"]
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False)
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(30), index=True, unique=True)
    alerts = db.relationship("Alert", backref="creator", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_url(self):
        return url_for("users.get_user", id=self.id, _external=True)

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
