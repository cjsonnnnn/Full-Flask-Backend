from flask_login import (
    login_required,
    login_user,
    logout_user,
)
import bcrypt
from flask import request, jsonify
from .. import db
from . import token_required, blacklist, generate_token, auth_bp
from ..models import Sales


# to regist a new sales
@auth_bp.route("/register", methods=["POST"])
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
@auth_bp.route("/login", methods=["POST"])
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
@auth_bp.route("/logout", methods=["POST"])
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
    