from flask_login import UserMixin
from ..main.models import Customer, Order, Cart
from .. import db


# primary tables
class Sales(db.Model, UserMixin):
    __tablename__ = "sales"
    username = db.Column(db.String(18), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(54), nullable=False)
    email = db.Column(db.String(27), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    # one to many relationship
    customers = db.relationship(Customer, backref="sales")        
    orders = db.relationship(Order, backref="sales")

    # one to one relationship
    cart = db.relationship(Cart, backref="sales", uselist=False)

    def get_id(self):
        return self.username