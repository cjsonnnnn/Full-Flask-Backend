from flask_login import LoginManager
from datetime import timedelta, datetime
from functools import wraps
from flask import request, jsonify, Blueprint
import jwt
from .. import app

# import modules
from . import endpoints
from . import models
from . import schema



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# login_manager.session_protection = "strong"
blacklist = set()           # Blacklist to store logged out tokens



# sales stuffs
@login_manager.user_loader
def load_user(username):
    return models.Sales.query.filter_by(username=username).first()


# to validate token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        
        if token in blacklist:
            return jsonify({'message': 'Token has been revoked!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = models.Sales.query.filter_by(username=data['username']).first()
        except:
            return jsonify({'message' : 'Token invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# to generate a JWT token
def generate_token(username):
    return jwt.encode(
        {'username' : username, 'exp' : datetime.utcnow() + timedelta(minutes=30)}, 
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )


# register blueprint
auth_bp = Blueprint('auth', __name__)
app.register_blueprint(auth_bp)