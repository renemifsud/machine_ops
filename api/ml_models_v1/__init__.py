from flask import Blueprint
from ..auth import auth_token

api = Blueprint('ml_models', __name__)


@api.before_request
@auth_token.login_required
def before_request():
    """All routes in this blueprint require authentication."""
    pass


from . import users, alerts, errors