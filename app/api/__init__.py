import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name):
    """Create an application instance."""
    app = Flask(__name__)

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://postgres:TestDBKey@localhost/machine_ops"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    with app.app_context():
        db.create_all()


    return app
