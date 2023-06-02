from .sales_persons import salesA, salesB
from app.main.models import Cart
from .. import db


# add their carts. Notice that, since it is one to one relationship (uselist=False), so we use a normal assign method, instead of append
cartA = Cart(qty=0); salesA.cart = cartA
cartB = Cart(qty=0); salesB.cart = cartB

# add to database
db.session.add_all([
    cartA, cartB
])
db.session.commit()
