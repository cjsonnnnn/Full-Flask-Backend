from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# import modules
from . import auth
from . import main



app = Flask(__name__)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "sales-ganteng"
app.config["co-password"] = "jasonganteng"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@127.0.0.1/sales"


db = SQLAlchemy(app)
ma = Marshmallow(app)