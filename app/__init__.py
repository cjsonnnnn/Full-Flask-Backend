from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
import os



app = Flask(__name__)
app.config.from_object(__name__)

# Load environment variables from .env file
load_dotenv()

# Load configuration values from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CO_PASSWORD'] = os.getenv('CO_PASSWORD')

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@127.0.0.1/sales"


db = SQLAlchemy(app)
ma = Marshmallow(app)


db = SQLAlchemy(app)
ma = Marshmallow(app)


# import modules
from . import configs
from . import models
from . import schemas
from . import auth
from . import main