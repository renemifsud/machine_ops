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
from flask_bootstrap import Bootstrap


db = SQLAlchemy()


def get_config_file(config_name):
    return os.path.join(os.getcwd(), "config", config_name + ".py")


def create_app():
    config_name = os.environ.get("APP_CONFIG", "development")
    app = Flask(__name__)
    Bootstrap(app)
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
    from .models import User

    with app.app_context():
        db.init_app(app)
        db.create_all()
        # populate the database
        if User.query.get(1) is None:
            u = User(username="renemifsud")
            u.set_password("renetest")
            db.session.add(u)
            db.session.commit()

    # authentication token route
    from app.auth import auth, verify_password

    @app.route("/", methods=["GET"])
    def app_root():
        if not session.get("logged_in"):
            return redirect("/login")
        else:
            return redirect("/app/home")

    @app.route("/login", methods=["GET", "POST"])
    def app_login():
        if request.method == "GET" and not session.get("logged_in"):
            return render_template("login.html")
        elif request.method == "GET" and session.get("token"):
            if User.verify_auth_token(session["token"]):
                return redirect("/home")

        elif request.method == "POST":
            if verify_password(request.form["username"], request.form["password"]):
                session["logged_in"] = True
                session["token"] = g.user.generate_auth_token()
                return redirect("/app/home")
        return render_template("login.html")

    @app.route("/get-auth-token/<int:seconds>")
    @auth.login_required
    def get_auth_token(seconds):
        return jsonify({"token": g.user.generate_auth_token(expires_in=seconds)})

    # Blueprints
    from app.main.routes import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/app")

    from app.users.routes import users as users_bp

    app.register_blueprint(users_bp, url_prefix="/")

    from app.alerts.routes import alerts as alerts_bp

    app.register_blueprint(alerts_bp, url_prefix="/")

    return app
