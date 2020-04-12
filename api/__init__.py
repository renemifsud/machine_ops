import os
from flask import Flask, jsonify, g
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name):
    """Create an application instance."""
    app = Flask(__name__)
    
    app.config.from_pyfile(get_config_file(config_name))

    db.init_app(app)

    #Blueprints
    from .api_v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    # authentication token route
    from .auth import auth
    @app.route('/get-auth-token')
    @auth.login_required
    def get_auth_token():
        return jsonify({'token': g.user.generate_auth_token()})

    return app

def get_config_file(config_name):
    return os.path.join(os.getcwd(), 'config', config_name + '.py')
    