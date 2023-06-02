from flask import Blueprint
from .. import app

# import modules
from . import endpoints
from . import models
from . import schema


main_bp = Blueprint('main', __name__)
app.register_blueprint(main_bp)