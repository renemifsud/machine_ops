import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = "postgres:TestDBKey@localhost:5432/machine_ops"

DEBUG = True
IGNORE_AUTH = False
SECRET_KEY = "top-secret!"
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://" + db_path
SESSION_COOKIE_HTTPONLY = False
JSONIFY_PRETTYPRINT_REGULAR = True

APP_URL = "http://127.0.0.1:5000"
APP_USER = "renemifsud"
APP_PASS = "renetest"

AWX_FQDN = "http://mo-awx.doxtechno.com"
AWX_USER = "admin"
AWX_PASSWORD = "Gl88jZKaPr8AZpBc0daY"

JOBS_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNTk1ODUwNzI4fQ.0EbfG3I_oFyFf9O3-4tEa5PiYrqh2WLTnsL6VE0VQxY"

JOBS = [
    {
        "id": "test",
        "func": "schedulers:job1",
        "args": (
            JOBS_KEY,
            AWX_FQDN,
            AWX_USER,
            AWX_PASSWORD,
            APP_URL,
            APP_USER,
            APP_PASS,
        ),
        "trigger": "interval",
        "seconds": 30,
        "replace_existing": True,
    }
]

SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}

SCHEDULER_EXECUTORS = {"default": {"type": "threadpool", "max_workers": 20}}

SCHEDULER_JOB_DEFAULTS = {"coalesce": False, "max_instances": 3}

SCHEDULER_API_ENABLED = True
