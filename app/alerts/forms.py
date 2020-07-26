from flask_wtf import FlaskForm
from wtforms import TextAreaField


class CreateAlert(FlaskForm):
    data = TextAreaField()
