import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = "postgres:TestDBKey@localhost:5432/machine_ops"

DEBUG = True
IGNORE_AUTH = False
SECRET_KEY = "top-secret!"
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://" + db_path
