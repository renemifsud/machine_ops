import os

from flask import (
    Flask,
    redirect,
    request,
    session,
    g,
    jsonify,
    render_template,
)
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_config_file(config_name):
    return os.path.join(os.getcwd(), "config", config_name + ".py")


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_pyfile(get_config_file(config_name))
    app.secret_key = "not so secret"
    CORS(
        app,
        origins="*",
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Credentials",
        ],
        supports_credentials=True,
    )

    # authentication token route
    from app.auth import auth, verify_password

    @app.route("/", methods=["GET"])
    def app_root():
        if not session.get("logged_in"):
            return redirect("/login")
        else:
            return redirect("/home")

    @app.route("/login", methods=["GET", "POST"])
    def app_login():
        if request.method == "GET" and not session.get("logged_in"):
            return render_template("login.html")
        elif request.method == "GET" and session.get("logged_in"):
            return redirect("/home")
        elif request.method == "POST":
            if verify_password(request.form["username"], request.form["password"]):
                session["logged_in"] = True
                session["token"] = g.user.generate_auth_token()
                return redirect("/home")
            else:
                return "Login Failed"
        return render_template("index.html")

    @app.route("/get-auth-token")
    @auth.login_required
    def get_auth_token():
        return jsonify({"token": g.user.generate_auth_token()})

    # Blueprints
    from app.main.routes import main as main_bp
    app.register_blueprint(main_bp, url_prefix="/")
  
    from app.users.routes import users as users_bp
    app.register_blueprint(users_bp, url_prefix="/")

    from app.alerts.routes import alerts as alerts_bp
    app.register_blueprint(alerts_bp, url_prefix="/")


    return app
