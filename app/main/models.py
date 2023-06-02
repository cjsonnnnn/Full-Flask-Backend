from .. import db
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy


# bridge tables
class DetailOrder(db.Model, UserMixin):
    __tablename__ = "detail_order"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="product_association")
    product = db.relationship("Product", back_populates="order_association")


class DetailCart(db.Model, UserMixin):
    __tablename__ = "detail_cart"
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False)

    cart = db.relationship("Cart", back_populates="product_association")
    product = db.relationship("Product", back_populates="cart_association")




# primary tables
class Customer(db.Model, UserMixin):
    __tablename__ = "customer"
    username = db.Column(db.String(18), primary_key=True)
    address = db.Column(db.String(99), nullable=False)
    img_link = db.Column(db.Text)

    sales_id = db.Column(db.String(18), db.ForeignKey("sales.username"), nullable=False)
    orders = db.relationship("Order", backref="customer")          # one to many relationship

    def get_id(self):
        return self.username


class Product(db.Model, UserMixin):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    available_qty = db.Column(db.Integer, nullable=False)
    ordered_qty = db.Column(db.Integer, nullable=False)
    total_qty = db.Column(db.Integer)
    promo = db.Column(db.Integer, nullable=False)
    img_link = db.Column(db.Text)

    order_association = db.relationship("DetailOrder", back_populates="product")
    orders = association_proxy("order_association", "order")                # many to many relationship

    cart_association = db.relationship("DetailCart", back_populates="product")
    carts = association_proxy("cart_association", "cart")                   # many to many relationship

    # warehouse_association = db.relationship("DetailWarehouse", back_populates="product")
    # warehouses = association_proxy("warehouse_association", "warehouse")    # many to many relationship

    # one to many relationship
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)

    # one to many relationship
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))


class Category(db.Model, UserMixin):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(18), nullable=False)

    products = db.relationship("Product", backref="category")


class Order(db.Model, UserMixin):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(27), nullable=False)
    status = db.Column(db.String(9), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer)
    sales_id = db.Column("sales_id", db.String(18), db.ForeignKey("sales.username"), nullable=False)
    customer_id = db.Column("customer_id", db.String(18), db.ForeignKey("customer.username"), nullable=False)

    product_association = db.relationship("DetailOrder", back_populates="order")
    products = association_proxy("product_association", "product")


class Cart(db.Model, UserMixin):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    sales_id = db.Column("sales_id", db.String(18), db.ForeignKey("sales.username"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    product_association = db.relationship("DetailCart", back_populates="cart")
    products = association_proxy("product_association", "product")


class Warehouse(db.Model, UserMixin):
    __tablename__ = "warehouse"
    id = db.Column(db.Integer, primary_key=True)
    ordered_qty = db.Column(db.Integer, nullable=False)
    available_qty = db.Column(db.Integer, nullable=False)
    total_qty = db.Column(db.Integer, nullable=False)

    # many to many relationship
    # product_association = db.relationship("DetailWarehouse", back_populates="warehouse")
    # products = association_proxy("product_association", "product")

    # one to many relationship
    products = db.relationship("Product", backref="warehouse")
