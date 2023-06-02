from .models import *
from . import ma


class SalesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sales
        include_fk = True


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_fk = True


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        include_fk = True


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        include_fk = True


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True


class DetailCartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DetailCart
        include_fk = True