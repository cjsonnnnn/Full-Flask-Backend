import socket
import bcrypt
from datetime import timedelta, datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow_sqlalchemy import SQLAlchemySchema
import mysql.connector
from sqlalchemy import text
import jwt
from functools import wraps


# init
app = Flask(__name__)
app.config.from_object(__name__)
app.config["SECRET_KEY"] = "sales-ganteng"
app.config["co-password"] = "jasonganteng"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@127.0.0.1/sales"
# app.config["SESSION_COOKIE_HTTPONLY"] = True
# app.config["REMEMBER_COOKIE_HTTPONLY"] = True
# app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.permanent_session_lifetime = timedelta(seconds=30)      

# CORS(
#     app, 
#     resources={r"/*":{'origins': "*"}},
#     expose_headers=["Content-Type", "X-CSRFToken"],
#     supports_credentials=True,
# )

# csrf = CSRFProtect(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)


# for login system
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# login_manager.session_protection = "strong"
blacklist = set()           # Blacklist to store logged out tokens





# database
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
class Sales(db.Model, UserMixin):
    __tablename__ = "sales"
    username = db.Column(db.String(18), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(54), nullable=False)
    email = db.Column(db.String(27), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)

    # one to many relationship
    customers = db.relationship("Customer", backref="sales")        
    orders = db.relationship("Order", backref="sales")

    # one to one relationship
    cart = db.relationship("Cart", backref="sales", uselist=False)

    def get_id(self):
        return self.username


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





# schemas
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_fk = True


class SalesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sales
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





# sales stuffs
@login_manager.user_loader
def load_user(username):
    return Sales.query.filter_by(username=username).first()


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
            current_user = Sales.query.filter_by(username=data['username']).first()
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





# api's/endpoints
# to get all products
@app.route("/getallproducts", methods=["GET"])
@token_required
def getAllProducts(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            products = Product.query.all()
            response_object["data"] = []

            for prd in products:
                response_object["data"].append({
                    "id": prd.id,
                    "name": prd.name,
                    "price": prd.price,
                    "description": prd.description,
                    "available_qty": prd.available_qty,
                    "ordered_qty": prd.ordered_qty,
                    "total_qty": prd.total_qty,
                    "promo": prd.promo,
                    "img_link": prd.img_link,
                    "category": Category.query.filter_by(id=prd.category_id).first().name,
                    "promo_price": int(prd.price-(prd.price * prd.promo / 100))
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)
        
        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get all available products
@app.route("/getallavailableproducts", methods=["GET"])
@token_required
def getAllAvailableProducts(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            available_products = Product.query.filter(Product.available_qty > 0).all()
            response_object["data"] = []

            for aprd in available_products:
                response_object["data"].append({
                    "id": aprd.id,
                    "name": aprd.name,
                    "price": aprd.price,
                    "description": aprd.description,
                    "available_qty": aprd.available_qty,
                    "ordered_qty": aprd.ordered_qty,
                    "total_qty": aprd.total_qty,
                    "promo": aprd.promo,
                    "img_link": aprd.img_link,
                    "category": Category.query.filter_by(id=aprd.category_id).first().name,
                    "promo_price": int(aprd.price-(aprd.price * aprd.promo / 100))
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)
        
        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)


# to get all promo products
@app.route("/getallpromos", methods=["GET"])
@token_required
def getAllPromos(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            promos = Product.query.filter((Product.promo > 0) & (Product.promo <= 100)).all()
            response_object["data"] = []

            for prd in promos:
                response_object["data"].append({
                    "id": prd.id,
                    "name": prd.name,
                    "price": prd.price,
                    "description": prd.description,
                    "available_qty": prd.available_qty,
                    "ordered_qty": prd.ordered_qty,
                    "total_qty": prd.total_qty,
                    "promo": prd.promo,
                    "img_link": prd.img_link,
                    "category": Category.query.filter_by(id=prd.category_id).first().name,
                    "promo_price": int(prd.price-(prd.price * prd.promo / 100))
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)
        
        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get all available products
@app.route("/getallavailablepromos", methods=["GET"])
@token_required
def getAllAvailablePromos(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            available_promos = Product.query.filter((Product.available_qty > 0) & (Product.promo > 0) & (Product.promo <= 100)).all()
            response_object["data"] = []

            for aprd in available_promos:
                response_object["data"].append({
                    "id": aprd.id,
                    "name": aprd.name,
                    "price": aprd.price,
                    "description": aprd.description,
                    "available_qty": aprd.available_qty,
                    "ordered_qty": aprd.ordered_qty,
                    "total_qty": aprd.total_qty,
                    "promo": aprd.promo,
                    "img_link": aprd.img_link,
                    "category": Category.query.filter_by(id=aprd.category_id).first().name,
                    "promo_price": int(aprd.price-(aprd.price * aprd.promo / 100))
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)
        
        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get all sales detail carts
@app.route("/getallcategories", methods=["GET"])
@token_required
def getAllCategories(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            # to get all detail carts
            theCategories = Category.query.all()
            response_object["data"] = [ctg.name for ctg in theCategories]

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)


# to get all sales orders [CLEAR]
@app.route("/getorders", methods=["GET"])
@token_required
def getOrders(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            orders = Order.query.filter_by(sales_id=current_user.username).all()
            response_object["data"] = []

            for ord in orders:
                response_object["data"].append({
                    "id": ord.id,
                    "image": Product.query.filter_by(id=DetailOrder.query.filter_by(order_id=ord.id).first().product_id).first().img_link,
                    "status": ord.status,
                    "total_price": ord.total_price,
                    "qty": ord.qty,
                    "customer": ord.customer_id,
                    "date": ord.date
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get detail order [CLEAR]
@app.route("/getdetailorder/<order_id>", methods=["GET"])
@token_required
def getDetailOrder(current_user, order_id):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            theOrder = Order.query.filter_by(sales_id=current_user.username, id=order_id).first()
            theDetailOrders = DetailOrder.query.filter_by(order_id=theOrder.id).all()
            response_object["data"] = {
                "customer": theOrder.customer_id,
                "total_price": theOrder.total_price,
                "total_qty": theOrder.qty,
                "date": theOrder.date,
                "detail_product": []
            }

            for dord in theDetailOrders:
                theProduct = Product.query.filter_by(id=dord.product_id).first()
                response_object["data"]["detail_product"].append({
                    "id": dord.id,
                    "name": theProduct.name,
                    "image": theProduct.img_link,
                    "qty": dord.qty,
                    "price": dord.qty*theProduct.price
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get all sales customers [CLEAR]
@app.route("/getcustomers", methods=["GET"])
@token_required
def getCustomers(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            customers = Customer.query.filter_by(sales_id=current_user.username).all()
            response_object["data"] = []

            for cus in customers:
                response_object["data"].append({
                    "address": cus.address,
                    "name": cus.username,
                    "img_link": cus.img_link,
                    "sales": Sales.query.filter_by(username=cus.sales_id).first().name
                })

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get sales data [CLEAR]
@app.route("/getsales", methods=["GET"])
@token_required
def getSales(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            response_object["data"] = {
                "username": current_user.username,
                "name": current_user.name,
                "email": current_user.email,
                "status": current_user.verified
            }

            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object := response_object["data"])
            # return jsonify(response_object)

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to get all information for cart page [CLEAR]
@app.route("/getdetailcarts", methods=["GET"])
@token_required
def getDetailCarts(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            theCart = Cart.query.filter_by(sales_id=current_user.username).first()
            # to check if the query results are available
            if (theCart != None):
                # to get all detail carts
                theDetailCarts = DetailCart.query.filter_by(cart_id=theCart.id).all()
                response_object["data"] = []

                for dc in theDetailCarts:
                    theProduct = Product.query.filter_by(id=dc.product_id).first()
                    response_object["data"].append({
                        "id": dc.id,
                        "qty": dc.qty,
                        "product_id": theProduct.id,
                        "is_available": dc.is_available,
                        "product_name": theProduct.name,
                        "product_description": theProduct.description,
                        "product_img": theProduct.img_link,
                        "product_price": theProduct.price,
                        "product_available_qty": theProduct.available_qty,
                        "product_category": Category.query.filter_by(id=theProduct.category_id).first().name,
                        "promo": theProduct.promo,
                        "promo_price": int(theProduct.price-(theProduct.price * theProduct.promo / 100))
                    })
                
                response_object["status"], response_object["message"] = "success", "-"
                return jsonify(response_object := response_object["data"])
                # return jsonify(response_object)
            else:
                response_object["message"] = "cart is missing"

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to check if a username for sales has been used or not
@app.route("/getchecksalesusername/<username>", methods=["GET"])
def getCheckSalesUsername(username):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "GET":
            # to get all detail carts
            theSales = Sales.query.filter_by(username=username).first()
            if (theSales == None):
                response_object["status"], response_object["message"] = "success", "-"
            else:
                response_object["message"] = "username has been used already"

            return jsonify(response_object)
            # return jsonify(response_object)

        return response_object
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to verify/unverify a sales
@app.route("/salesverifyunverify", methods=["PATCH"])
def salesVerifyUnverify():
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "PATCH":
            data = request.get_json()
            sales_username = data.get("sales_username")
            co_password = data.get("co-password")
            order = data.get("order")

            # defining
            theSales = Sales.query.filter_by(username=sales_username).first()

            # to check if the query results are available
            if (theSales != None):     
                if (co_password == app.config["co-password"]):
                    if (theSales.verified):
                        if (order == "verify"):
                            response_object["message"] = "the sales is verified already"
                        elif (order == "unverify"):
                            theSales.verified = False
                            db.session.commit()
                            response_object["status"], response_object["message"] = "success", "-"
                            return jsonify(response_object)
                        else:
                            response_object["message"] = "invalid order"
                    else:
                        if (order == "verify"):
                            theSales.verified = True
                            db.session.commit()
                            response_object["status"], response_object["message"] = "success", "-"
                            return jsonify(response_object)
                        elif (order == "unverify"):
                            response_object["message"] = "the sales is unverified already"
                        else:
                            response_object["message"] = "invalid order"
                else:
                    response_object["message"] = "you are not authorized to make this call" 
            else:
                response_object["message"] = "sales is missing"
                
        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)


# to unsubscribe a customer to a sales
@app.route("/unsubscribe", methods=["PATCH"])
@token_required
def unsubscribe(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "PATCH":
            data = request.get_json()
            customer_username = data.get("customer_username")

            # defining
            theCustomer = Customer.query.filter_by(username=customer_username).first()

            # to check if the query results are available
            if (theCustomer != None):
                # to check whether or not the customer is already unsubscribed the Sales
                if (theCustomer in current_user.customers):        
                    current_user.customers.remove(theCustomer)
                    db.session.delete(theCustomer)
                    db.session.commit()
                    response_object["status"], response_object["message"] = "success", "-"
                    return jsonify(response_object)
                else:
                    response_object["message"] = "the customer is already unsubscribed the sales"
            else:
                response_object["message"] = "the customer is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to confirm an order
@app.route("/confirmorder", methods=["PATCH"])
def confirmOrder():
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "PATCH":
            data = request.get_json()
            order_id = data.get("order_id")
            sales_id = data.get("sales_username")

            # defining
            theOrder = Order.query.filter_by(id=order_id, sales_id=sales_id).first()

            # to check if the query result is available
            if theOrder != None:
                # to check whether or not the order is active
                if (theOrder.status == "active"):        
                    theOrder.status = "sent"        # update order status

                    db.session.commit()
                    response_object["status"], response_object["message"] = "success", "-"
                    return jsonify(response_object)
                else:
                    response_object["message"] = f"the order is already {theOrder.status}"
            else:
                response_object["message"] = "the order is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to confirm an order
@app.route("/cancelorder", methods=["PATCH"])
def cancelOrder():
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "PATCH":
            data = request.get_json()
            sales_id = data.get("sales_username")
            order_id = data.get("order_id")

            # defining
            theOrder = Order.query.filter_by(id=order_id, sales_id=sales_id).first()

            # to check if the query result is available
            if theOrder != None:
                # to check whether or not the order is active
                if (theOrder.status == "active"):        
                    # update product stock
                    for product in theOrder.products:
                        product.available_qty += DetailOrder.query.filter_by(order_id=order_id, product_id=product.id).first().qty

                    # update order status
                    theOrder.status = "canceled"        

                    db.session.commit()
                    response_object["status"], response_object["message"] = "success", "-"
                    return jsonify(response_object)
                else:
                    response_object["message"] = f"the order is already {theOrder.status}"
            else:
                response_object["message"] = "the order is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to confirm an order [CLEAR]
@app.route("/updatedetailcarts", methods=["PATCH"])
@token_required
def updateDetailCarts(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "PATCH":
            data = request.get_json()
            updated_detail_carts = data.get("updated_detail_carts")

            # update the updated detail carts
            for newdc in updated_detail_carts:
                theDetailCart = DetailCart.query.filter_by(id=newdc["id"]).first()
                
                if (theDetailCart == None):
                    raise Exception("some of detail cart ids are invalid")
                
                theProduct = Product.query.filter_by(id=theDetailCart.product_id).first()

                theDetailCart.qty = newdc["qty"] if (theProduct.available_qty >= newdc["qty"]) else theProduct.available_qty     

            db.session.commit()
            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object)

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to regist a new sales
@app.route("/register", methods=["POST"])
def register():
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            name = data.get("name")
            email = data.get("email")

            # defining
            theSalesUsername = Sales.query.filter_by(username=username).first()
            theSalesPassword = Sales.query.filter_by(password=password).first()

            # to check if the query result is available
            if (theSalesUsername == None) & (theSalesPassword == None):
                # registering
                newSales = Sales(
                    username=username, 
                    name=name, 
                    password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), 
                    email=email, 
                    verified=False
                )
                db.session.add(newSales)
                db.session.commit()
                response_object["status"], response_object["message"] = "success", "-"
                return jsonify(response_object)
            else:
                response_object["message"] = "either username or password has been used already"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)


# to login a sales
@app.route("/login", methods=["POST"])
def login():
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            # defining
            theSales = Sales.query.filter_by(username=username).first()

            # to check if the query result is available
            if theSales != None:
                # check if password is valid
                if (bcrypt.checkpw(password.encode("utf-8"), theSales.password.encode('utf-8'))):
                    # check if the sales is verified or not
                    if theSales.verified == 1:
                        # login the sales
                        login_user(theSales)
                        
                        # get a JWT token
                        token = generate_token(theSales.username)
                        return jsonify({'token' : token})
                    else:
                        response_object["message"] = "the sales is not verified yet"
                else:
                    response_object["message"] = "password invalid"
            else:
                response_object["message"] = "either username or password inputted is invalid"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to logout a sales
@app.route("/logout", methods=["POST"])
@token_required
@login_required
def logout(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            # logout the sales
            token = request.headers['x-access-token']
            blacklist.add(token)
            logout_user()
            response_object["status"], response_object["message"] = "success", "-"
            return jsonify(response_object)

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to add new customer
@app.route("/addnewcustomer", methods=["POST"])
@token_required
def addNewCustomer(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            customer_username = data.get("customer_username")
            customer_address = data.get("customer_address")
            customer_img_link = data.get("customer_img_link")

            # defining
            theCustomer = Customer.query.filter_by(username=customer_username).first()

            # to check if the query results are available
            if (theCustomer == None):
                newCustomer = Customer(username=customer_username, address=customer_address, img_link=customer_img_link, sales_id=current_user.username)
                db.session.add(newCustomer)
                db.session.commit()
                response_object["status"], response_object["message"] = "success", "-"
                return jsonify(response_object)
            else:
                response_object["message"] = "customer is already registered"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)


# to add an order
@app.route("/addorder", methods=["POST"])
@token_required
def addOrder(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            customer_username = data.get("customer_username")
            cartproductids = data.get("cartproductids")

            # defining
            theCustomer = Customer.query.filter_by(username=customer_username).first()
            theCart = Cart.query.filter_by(sales_id=current_user.username).first()
            theCartProducts = [
                DetailCart.query.filter_by(
                    id=cartproductid, cart_id=theCart.id
                ).first() for cartproductid in cartproductids
            ]

            # to check if the query results are available
            if (theCustomer != None) & (None not in theCartProducts):
                # to check if the customer inputted is already subscribed the sales
                if (theCustomer in current_user.customers):
                    # create an order
                    curdate = str(datetime.now().strftime(f"%d-%m-%Y"))
                    anOrder = Order(date=curdate, status="active", sales_id=current_user.username, customer_id=theCustomer.username, total_price=0)
                    db.session.add(anOrder)
                    db.session.commit()

                    newTotalPrice = 0

                    # create the detail
                    for cartProduct in theCartProducts:
                        theProduct = Product.query.filter_by(id=cartProduct.product_id).first()
                        theDetailOrder = DetailOrder(qty=cartProduct.qty, order_id=anOrder.id, product_id=theProduct.id)
                        db.session.add(theDetailOrder)

                        # update product stock
                        theProduct.available_qty -= cartProduct.qty if (cartProduct.qty <= theProduct.available_qty) else theProduct.available_qty

                        # remove the cart product
                        db.session.delete(cartProduct)

                        # update total price
                        if (theProduct.promo > 0):
                            newTotalPrice += int(theProduct.price - (theProduct.price * theProduct.promo / 100))*cartProduct.qty
                        else:
                            newTotalPrice += (theProduct.price*cartProduct.qty)

                    # update the total price in order
                    anOrder.total_price = newTotalPrice

                    db.session.commit()
                    response_object["status"], response_object["message"] = "success", "-"
                    return jsonify(response_object)
                else:
                    response_object["message"] = "the customer is not subscribed the sales yet"
            else:
                response_object["message"] = "either customer or list of cartproducts is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to add certain number of product to the cart 
@app.route("/addcartproduct", methods=["POST"])
@token_required
def addCartProduct(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            product_id = data.get("product_id")
            qty = data.get("qty")

            # defining
            theCart = Cart.query.filter_by(sales_id=current_user.username).first()
            theProduct = Product.query.filter_by(id=product_id).first()

            # to check if the query results are available
            if (theCart != None) & (theProduct != None):
                # to check if the product is already in the cart
                if (theDetailCart := DetailCart.query.filter_by(cart_id=theCart.id, product_id=theProduct.id).first()) != None:
                    theDetailCart.qty += qty if (theProduct.available_qty-theDetailCart.qty) >= qty else theProduct.available_qty-theDetailCart.qty
                else:
                    # to make sure if the product stock is 0, then it can not be added to the cart
                    if (theProduct.available_qty > 0):
                        # add the product to the cart
                        theDetailCart = DetailCart(qty=qty if theProduct.available_qty >= qty else theProduct.available_qty, is_available=True, cart_id=theCart.id, product_id=theProduct.id)
                        db.session.add(theDetailCart)
                    else:
                        response_object["message"] = "the product stock is not available"
                        return jsonify(response_object)
                        
                db.session.commit()
                response_object["status"], response_object["message"] = "success", "-"
                return jsonify(response_object)
            else:
                response_object["message"] = "either cart or product is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to reduce certain number of product from the cart 
@app.route("/reducecartproduct", methods=["POST"])
@token_required
def reduceCartProduct(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            product_id = data.get("product_id")
            qty = data.get("qty")

            # defining
            theCart = Cart.query.filter_by(sales_id=current_user.username).first()
            theProduct = Product.query.filter_by(id=product_id).first()

            # to check if the query results are available
            if (theCart != None) & (theProduct != None):
                # to check if the product is already in the cart
                if (theDetailCart := DetailCart.query.filter_by(cart_id=theCart.id, product_id=theProduct.id).first()) != None:
                    if theDetailCart.qty > qty:
                        theDetailCart.qty -= qty if theDetailCart.qty >= qty else theDetailCart.qty
                    else:
                        db.session.delete(theDetailCart)
                    
                    db.session.commit()
                    response_object["status"], response_object["message"] = "success", "-"
                else:
                    response_object["message"] = "the product has already been removed from the cart"
                        
                return jsonify(response_object)
            else:
                response_object["message"] = "either cart or product is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to remove certain product from the cart 
@app.route("/removecartproduct", methods=["POST"])
@token_required
def removeCartProduct(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            data = request.get_json()
            product_id = data.get("product_id")

            # defining
            theCart = Cart.query.filter_by(sales_id=current_user.username).first()
            theProduct = Product.query.filter_by(id=product_id).first()

            # to check if the query results are available
            if (theCart != None) & (theProduct != None):
                # to check if the product is already in the cart
                if (theDetailCart := DetailCart.query.filter_by(cart_id=theCart.id, product_id=theProduct.id).first()) != None:
                    # remove the product from the cart
                    db.session.delete(theDetailCart)

                    db.session.commit()
                    response_object["status"], response_object["message"] = "success", "-"
                else:
                    response_object["message"] = "product is not in the cart"
                        
                return jsonify(response_object)
            else:
                response_object["message"] = "either cart or product is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)
    

# to remove all detail carts 
@app.route("/removeallcartproduct", methods=["POST"])
@token_required
def removeAllCartProduct(current_user):
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        if request.method == "POST":
            # defining
            theCart = Cart.query.filter_by(sales_id=current_user.username).first()

            # to check if the query results are available
            if (theCart != None):
                theDetailCarts = DetailCart.query.filter_by(cart_id=theCart.id).all()
                
                if (theDetailCarts == []):
                    response_object["message"] = "the cart is already empty"                        
                    return jsonify(response_object)
                
                for dc in theDetailCarts:
                    db.session.delete(dc)

                db.session.commit()
                response_object["status"], response_object["message"] = "success", "-"                        
                return jsonify(response_object)
            else:
                response_object["message"] = "either cart or product is missing"

        return jsonify(response_object)
    except Exception as e:
         response_object["message"] = str(e)
         return jsonify(response_object)




# initializing data and stuffs
@app.route("/")
def InitializeData():
    response_object = {
        "status": "fail",
        "message": "error occured"
    }

    try:
        # add an sales
        salesA = Sales(
            username="salesA", 
            name="Suhendra", 
            password=bcrypt.hashpw("sA".encode('utf-8'), bcrypt.gensalt()), 
            email="jpiay40@students.calvin.ac.id", 
            verified=True
        )
        salesB = Sales(
            username="salesB", 
            name="Siti", 
            password=bcrypt.hashpw("sB".encode('utf-8'), bcrypt.gensalt()), 
            email="cjsonnnnn@gmail.com", 
            verified=False
        )

        # add their carts. Notice that, since it is one to one relationship (uselist=False), so we use a normal assign method, instead of append
        cartA = Cart(qty=0); salesA.cart = cartA
        cartB = Cart(qty=0); salesB.cart = cartB

        # add customers
        cusA = Customer(
            username="cusA", 
            address="SHINJUKU EASTSIDE SQUARE 6-27-30 Shinjuku, Shinjuku-ku, Tokyo 160-8430, Japan",
            img_link="https://cdn.medcom.id/dynamic/content/2022/06/19/1440278/r7gTknhVI2.jpg?w=480",
            sales_id=salesA.username
        )
        cusB = Customer(
            username="cusB", 
            address="Residence No. 55 Central Luxury Mansion",
            img_link="https://helpx.adobe.com/content/dam/help/en/illustrator/how-to/character-design/jcr_content/main-pars/image/character-design-intro_900x506.jpg.img.jpg",
            sales_id=salesA.username
        )
        cusC = Customer(
            username="cusC", 
            address="2 Chome-8-1 Nagao, Tama Ward, Kawasaki Prefecture, Kanagawa 214-0023, Japan",
            img_link="https://lumiere-a.akamaihd.net/v1/images/ct_belle_upcportalreskin_20694_e5816813.jpeg?region=0,0,330,330",
            sales_id=salesB.username
        )
        

        # execute sales and customer data
        db.session.add_all([
            salesA, salesB,
            cusA, cusB, 
            cusC
        ])
        db.session.commit()


        # define a warehouse
        theWarehouse = Warehouse(
            ordered_qty = 0,
            available_qty = 0,
            total_qty = 0
        )
        
        # execute warehouse
        db.session.add(theWarehouse)
        db.session.commit()


        # add categories
        catA = Category(name="beverages")
        catB = Category(name="foods")
        catC = Category(name="cleaning product")


        # execute categories
        db.session.add_all([catA, catB, catC])
        db.session.commit()


        # add products
        prdA = Product(
            name="Indomie Mi Instan Goreng Plus Special 85G",
            price=3100,
            description="Mi goreng yang lezat dan nikmat, terbuat dari bahan berkualitas dan rempah rempah terbaik.",
            available_qty=36,
            ordered_qty=0,
            total_qty=36,
            promo=0,
            img_link = "https://assets.klikindomaret.com/products/10003517/10003517_1.jpg",
            warehouse_id = theWarehouse.id,
            category_id= catA.id
        )
        prdB = Product(
            name="Sunlight Pencuci Piring Lime 420mL",
            price=9900,
            description="Sunlight Jeruk Nipis 100 mampu menghilangkan lemak dengan kekuatan 100 jeruk nipis di tiap kemasannya, secara aktif mengangkat dan menghilangkan lemak membandel, dan juga membersihkan dengan cepat berkat teknologi baru Cepat Bilas.",
            available_qty=3,
            ordered_qty=0,
            total_qty=3,
            promo=27,
            img_link = "https://assets.klikindomaret.com/products/20112492/20112492_1.jpg",
            warehouse_id = theWarehouse.id,
            category_id= catC.id
        )
        prdC = Product(
            name="Bear Brand Susu Encer Steril 189Ml",
            price=7300,
            description=f"Bear brand terbuat dari 100% susu sapi steril murni. Susu steril dianjurkan untuk setiap kegunaan yang membutuhkan susu dan dapat di konsumsi setiap hari sesuai kebutuhan.",
            available_qty=6,
            ordered_qty=0,
            total_qty=6,
            promo=45,
            img_link = "https://assets.klikindomaret.com/promos/20230517_07_00_20230523_23_00/10004906/10004906_1.jpg",
            warehouse_id = theWarehouse.id,
            category_id= catB.id
        )
        prdD = Product(
            name="Khong Guan Biscuit Red Segi Assorted 1600G",
            price=91500,
            description="Khong guan biskuit dengan kualitas terbaik, berbagai bentuk dan rasa yang enak didalamnya.",
            available_qty=312,
            ordered_qty=0,
            total_qty=312,
            promo=72,
            img_link = "https://assets.klikindomaret.com/products/10000360/10000360_1.jpg",
            warehouse_id = theWarehouse.id,
            category_id= catB.id
        )
        prdE = Product(
            name="Nescafe Coffee Drink Caramel Macchiato 220Ml",
            price=7000,
            description="Rasakan sensasi minuman kualitas Ala Caf kapan saja dan dimana saja didalam satu kemasan kaleng Nescaf Ala Caf. Dengan tiga varian rasa baru yaitu Latte, Cappucino, dan Caramel Macchiato, kenikmatan minuman caf kini bisa dinikmati oleh siapa saja. Perpadu",
            available_qty=35,
            ordered_qty=0,
            total_qty=35,
            promo=18,
            img_link = "https://assets.klikindomaret.com/products/20114494/20114494_1.jpg",
            warehouse_id = theWarehouse.id,
            category_id= catA.id
        )
        prdF = Product(
            name="So Klin Pembersih Lantai Sereh 780Ml",
            price=10900,
            description="SO KLIN Pembersih Lantai Sereh Lemon Grass merupakan cairan pembersih lantai yang di rancang khusus untuk memudahkan Anda dalam membersihkan lantai rumah. Cairan pembersih lantai persembahan SOKLIN ini secara efektif membersihkan seluruh permukaan lantai.",
            available_qty=463,
            ordered_qty=0,
            total_qty=463,
            promo=0,
            img_link = "https://assets.klikindomaret.com/products/20101095/20101095_1.jpg",
            warehouse_id = theWarehouse.id,
            category_id= catB.id
        )

        # execute product data
        db.session.add_all([
            prdA, prdB, prdC, prdD, prdE, prdF
        ])
        db.session.commit()

        response_object["status"], response_object["message"]  = "success", "all data has been successfully added"
    except Exception as e:
        db.session.rollback()
        response_object["status"], response_object["message"] = "fail", str(e)

    return jsonify(response_object)


# to automatically create a new database, in case it does not exist
def create_database():
    # create the database
    conn = mysql.connector.connect(user='root', password='', host='localhost')
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS sales')
    conn.commit()
    conn.close()


# define some triggers
triggers = [
    # to update qty in cart based on number of detail_carts
    """
    CREATE TRIGGER update_cart_qty_on_insert_detail_cart_trigger 
    AFTER INSERT
    ON detail_cart
    FOR EACH ROW 
    BEGIN
        DECLARE cart_qty_insert INTEGER;
        SELECT COUNT(*) INTO cart_qty_insert FROM detail_cart WHERE cart_id = NEW.cart_id;
        UPDATE cart SET qty = cart_qty_insert WHERE id = NEW.cart_id;
    END
    """,
    # to update qty in cart based on number of detail_carts
    """
    CREATE TRIGGER update_cart_qty_on_delete_detail_cart_trigger 
    AFTER DELETE
    ON detail_cart
    FOR EACH ROW 
    BEGIN  
        DECLARE cart_qty_delete INTEGER;
        SELECT COUNT(*) INTO cart_qty_delete FROM detail_cart WHERE cart_id = OLD.cart_id;
        UPDATE cart SET qty = cart_qty_delete WHERE id = OLD.cart_id;
    END
    """,
    # to update is_available in detail_cart based on qty in product
    """
    CREATE TRIGGER update_detail_cart_is_available_on_update_product_trigger 
    AFTER UPDATE
    ON product
    FOR EACH ROW 
    BEGIN
        UPDATE detail_cart
        SET is_available = CASE
            WHEN (SELECT available_qty FROM product WHERE id = NEW.id) > 0 THEN 1
            ELSE 0
            END
        WHERE product_id = NEW.id;
    END;
    """,
    # to update qty in detail_cart based on product qty
    """
    CREATE TRIGGER update_detail_cart_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        IF NEW.available_qty != OLD.available_qty THEN
            UPDATE detail_cart cd
            SET cd.qty = CASE
                            WHEN cd.qty > NEW.available_qty THEN NEW.available_qty
                            ELSE cd.qty
                        END
            WHERE cd.product_id = NEW.id;
        END IF;
    END;
    """,
    # to update ordered_qty in product everytime insertion on detail_order
    """
    CREATE TRIGGER update_product_ordered_qty_on_insert_detail_order_trigger
    AFTER INSERT 
    ON detail_order
    FOR EACH ROW
    BEGIN
        UPDATE product p
        SET p.ordered_qty = (
            SELECT SUM(qty) 
            FROM detail_order 
            WHERE order_id IN (
                SELECT id 
                FROM `order` 
                WHERE status IN ('active', 'sent')
            ) AND product_id = NEW.product_id
        )
        WHERE p.id = NEW.product_id;
    END;
    """,
    # to update qty in order based on insertion on detail_order
    """
    CREATE TRIGGER update_order_qty_on_insert_detail_order_trigger
    AFTER INSERT 
    ON detail_order
    FOR EACH ROW
    BEGIN
        UPDATE `order` o
        SET o.qty = (
            SELECT COUNT(*)
            FROM detail_order
            WHERE order_id = o.id
        )
        WHERE o.id = NEW.order_id;
    END;
    """,
    # to update ordered_qty in product everytime updation on order
    """
    CREATE TRIGGER update_product_ordered_qty_on_update_order_trigger
    AFTER UPDATE 
    ON `order`
    FOR EACH ROW
    BEGIN
        UPDATE product p
        SET p.ordered_qty = (
            SELECT SUM(qty)
            FROM detail_order
            WHERE order_id IN (
                SELECT id 
                FROM `order` 
                WHERE status IN ('active', 'sent')
            ) AND product_id = p.id
        )
        WHERE p.id IN (SELECT product_id from detail_order WHERE order_id=NEW.id);
    END;
    """,
    # to update total_qty in product everytime updation on product
    """
    CREATE TRIGGER update_product_total_qty_on_update_product_trigger
    BEFORE UPDATE 
    ON product
    FOR EACH ROW
    SET NEW.total_qty = COALESCE(NEW.ordered_qty, 0) + COALESCE(NEW.available_qty, 0);
    """,
    # to update available_qty in warehouse based on product available_qty
    """
    CREATE TRIGGER update_warehouse_available_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        UPDATE warehouse w
        SET w.available_qty = (SELECT SUM(available_qty) FROM `product`);
    END;
    """,
    # to update ordered_qty in warehouse based on product ordered_qty
    """
    CREATE TRIGGER update_warehouse_ordered_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        UPDATE warehouse w
        SET w.ordered_qty = (SELECT SUM(ordered_qty) FROM `product`);
    END;
    """,
    # to update total_qty in warehouse based on product total_qty
    """
    CREATE TRIGGER update_warehouse_total_qty_on_update_product_trigger
    AFTER UPDATE 
    ON product
    FOR EACH ROW
    BEGIN
        UPDATE warehouse w
        SET w.total_qty = (SELECT SUM(total_qty) FROM `product`);
    END;
    """,
]


# to put the triggers in to database
def create_triggers():
    with db.engine.connect() as con:
        try:
            for trigger in triggers:
                con.execute(text(trigger))
        except Exception as e:
            pass


if __name__ == "__main__":
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    with app.app_context():
        create_database()       # to define all orm database
        db.create_all()         # insert those to db, which is mysql
        create_triggers()       # insert triggers to db
        InitializeData()        # initialize some data to the db
        
    app.run(port=5000,debug=True,threaded=False,host=ip_address)
    # app.run()


    # hashed_password = bcrypt.hashpw("hai".encode('utf-8'), bcrypt.gensalt())
    # result = bcrypt.checkpw("hai".encode('utf-8'), hashed_password)
    # print(result)









# quick information and tips:
# - for the sake of implementing a best practice, we do not assign a value to the attributes that are either PK or FK manually... but I just realized, that it means I can't define the column as nullable=False. So... yeah, nvm
# - backref will create an extra column to the target in database
# - the difference between PATCH and POST is based on whether or not the number of rows is changing
# add this => def get_id(self), in order to use other than id as the PK
# don't output raw table, but customize it as what's needed



# task: cors! 1
# last updated: 29/05/23; 01:24





# note
# this app response format is being adapted to current project which requires the 'status' and 'message' to be not displayed... so the end of return, the respond would be `return response jsonify(response_object := response_object["data"])`.