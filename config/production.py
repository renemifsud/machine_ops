import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = "postgres:TestDBKey@postgres_db:5432/machine_ops"

DEBUG = True
IGNORE_AUTH = False
SECRET_KEY = "top-secret!"
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://" + db_path
SQLALCHEMY_TRACK_MODIFICATIONS = True
JSONIFY_PRETTYPRINT_REGULAR = True
