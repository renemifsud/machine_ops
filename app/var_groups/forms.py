from flask_wtf import FlaskForm
from wtforms import SelectField
from app.models import Var_Group


class CreateVarGroup(FlaskForm):
    solutions_list = SelectField("solution", choices=[])
