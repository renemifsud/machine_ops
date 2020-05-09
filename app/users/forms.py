from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

class CreateUser(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    conf_pass = PasswordField('conf_pass')
    