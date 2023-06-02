from flask import Blueprint
from .. import app


# define blueprint
main_bp = Blueprint('main', __name__)


# import modules
from . import endpoints


# register blueprint
app.register_blueprint(main_bp)