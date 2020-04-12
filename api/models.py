from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for, current_app
import json


class ValidateionError(ValueError):
    pass


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False)
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(30), index=True, unique=True)
    alerts = db.relationship('Alert', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_url(self):
        return url_for("api.get_user", id=self.id, _external=True)

    def export_data(self):
        return {"self_url": self.get_url(), "username": self.username}

    def check_import(self, data):
        try:
            self.username = data["username"]
            self.email = data["email"]
            self.set_password(data["password"])
        except KeyError as e:
            raise ValidateionError("Invalid 'User', missing " + e.args[0])
        return self

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id, 'hash': self.password_hash}).decode('utf-8')


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(500), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            index=True)

    def get_url(self):
        return url_for("api.get_alert", id=self.id, _external=True)

    def export_data(self):
        return {"id": self.id, "self_url": self.get_url()}

    def check_import(self, data):
        try:
            self.user_id
            self.data = json.dumps(data)
        except KeyError as e:
            raise ValidateionError("The alert is not JSON Serialisable")
        return self




