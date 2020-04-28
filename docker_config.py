import os

DEBUG = True
SECRET_KEY = "TestKey"
SQLALCHEMY_DATABASE_URI = "postgresql://"+os.environ['POSTGRES_USER']+":"+os.environ['POSTGRES_PASSWORD']+"@127.0.0.1/" + os.environ['POSTGRES_DB']