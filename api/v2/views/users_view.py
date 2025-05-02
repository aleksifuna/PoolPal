#!/usr/bin/env python3
"""
View for User object that handles all RESTFul API actions
"""
from flask import jsonify, request, Blueprint, make_response
from api.v2.models.user import User
from api.v2.models.user import DriverDetails
from api.v2.utils import hash_password, send_email, generate_uuid

from datetime import datetime
import bcrypt


from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


users_blueprint = Blueprint("user", __name__)


@users_blueprint.route("/users", methods=["POST"], strict_slashes=False)
def register_user():
    """
    Registers a user
    """
    if not request.json:
        return jsonify({"error": "Not a JSON"}), 400
    data = request.json
    required = ["first_name", "email", "phone", "password"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400
    if User.objects(email=data["email"]).first():
        return jsonify({"error": "User already Exists"}), 400
    data["password"] = hash_password(data["password"])
    user = User()
    for key, value in data.items():
        setattr(user, key, value)
    user.save()
    uuid = generate_uuid()
    setattr(user, "confirmation_token", uuid)
    user.save()
    confirmation_endpoint = "http://127.0.0.1:5000/api/v1/users/confirmations"
    msg = f"click {confirmation_endpoint}/{uuid} to verify account"
    if send_email(user.email, "Verify Account", msg):
        pass
    return jsonify(user.todict()), 201


@users_blueprint.route("/users/<user_id>", methods=["GET"], strict_slashes=False)
def get_user(user_id):
    """
    Returns the details of a user
    """
    user = User.objects(id=user_id).first()
    if user:
        return jsonify(user.todict()), 200
    return jsonify({"error": "Not Found"}), 404


@users_blueprint.route("/users/<user_id>", methods=["PUT"], strict_slashes=False)
@jwt_required()
def update_user(user_id):
    """
    Updates the details of the user
    """
    identity = get_jwt_identity()
    if user_id != identity:
        return jsonify({"error": "unauthorized"}), 401
    editable = [
        "first_name",
        "last_name",
        "phone",
        "preferences",
        "profile_picture",
        "role",
    ]
    data = request.json
    if not data:
        return jsonify({"error": "Not a JSON"}), 400
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "Not Found"}), 404
    for key, value in data.items():
        if key not in editable:
            return jsonify({"error": f"{key} cant be changed"}), 400
        setattr(user, key, value)
    user.updated_at = datetime.now()
    user.save()
    return jsonify(user.todict()), 200


@users_blueprint.route(
    "/users/<user_id>/driver", methods=["POST"], strict_slashes=False
)
@jwt_required()
def add_driver_details(user_id):
    identity = get_jwt_identity()
    if user_id != identity:
        return jsonify({"error": "unauthorized"}), 401
    data = request.json
    if not data:
        return jsonify({"error": "Not a JSON"}), 400
    required = ["car_model", "car_number_plate", "license_number"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} missing"}), 400
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User Not Found"}), 404
    if user.role == "passenger":
        return jsonify({"error": "Action can only be perfomed by drivers"}), 401
    if user.driver_details:
        return jsonify({"error": "Driver details already set"}), 400
    driver_dets = DriverDetails()
    for key, value in data.items():
        setattr(driver_dets, key, value)
    setattr(user, "driver_details", driver_dets)
    user.save()
    return jsonify(user.todict()), 201


@users_blueprint.route("/users/<user_id>/driver", methods=["PUT"], strict_slashes=False)
@jwt_required()
def update_driver_details(user_id):
    identity = get_jwt_identity()
    if user_id != identity:
        return jsonify({"error": "unauthorized"}), 401
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User Not Found"}), 404
    if user.role == "passenger":
        return jsonify({"error": "Action can only be perfomed by drivers"}), 401
    if not user.driver_details:
        return jsonify({"error": "No driver details set"}), 400
    data = request.json
    if not data:
        return jsonify({"error": "Not a JSON"}), 400
    required = ["car_model", "car_number_plate", "license_number"]
    update_dict = {}
    for key, value in data.items():
        if key not in required:
            return jsonify({"error": f"Cannot update {key}"}), 400
        update_dict[f"set__driver_details__{key}"] = value
    user.update(**update_dict)
    user.updated_at = datetime.now()
    user.save()
    user.reload()
    return jsonify(user.todict()), 200


@users_blueprint.route("/users/auth_token", methods=["POST"], strict_slashes=False)
def user_login():
    """
    Creates authorization token for the user to login
    """
    data = request.json
    if not data:
        return jsonify({"error": "Not a JSON"}), 400
    required = ["email", "password"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is missing"}), 400
    user = User.objects(email=data["email"]).first()
    if not user:
        return jsonify({"error": "User Not Found"}), 404
    if not bcrypt.checkpw(data["password"].encode("utf-8"), user.password):
        return jsonify({"error": "Wrong Email or Password"}), 400
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    response = make_response(jsonify(access_token=access_token))
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 15,
        path="/api/v2/users/refesh_token",
        secure=False,
        samesite="Strict",
    )
    return response, 200


@users_blueprint.route("/users/refresh_token", methods=["GET"], strict_slashes=False)
@jwt_required(refresh=True)
def refresh_token():
    """
    Refreshes the access token
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    response = make_response(jsonify(access_token=access_token))
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        max_age=0,
        path="/api/v2/users/refresh_token",
        secure=False,
        samesite="Strict",
    )
    return response, 200


@users_blueprint.route("/users/logout", methods=["DELETE"], strict_slashes=False)
@jwt_required()
def logout():
    """
    Logs out the user
    """
    response = make_response(jsonify({"message": "Logged Out"}))
    response.set_cookie(
        "refresh_token",
        "",
        httponly=True,
        max_age=0,
        path="/api/v2/users/refresh_token",
        secure=False,
        samesite="Strict",
    )
    return response, 200


@users_blueprint.route(
    "/users/confirmations/<uuid>", methods=["GET"], strict_slashes=False
)
@jwt_required()
def confirm_account(uuid):
    """
    Verifies account with uuid
    """
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({"error": "User Not Found"}), 404
    if str(user.confirmation_token) == uuid:
        setattr(user, "account_verified", True)
        user.save()
        user.update(unset__confirmation_token=1)
        return jsonify({"Message": "Account Verfied"}), 200
    return jsonify({"error": "Verification Failed"}), 400


@users_blueprint.route("/users/reset_token", methods=["POST"], strict_slashes=False)
def reset_password_token():
    """
    Generates password reset token and sends it via email
    """
    data = request.json
    if not data:
        return jsonify({"error": "Not a Json"}), 400
    uuid = generate_uuid()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email not Found"})
    user = User.objects(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    setattr(user, "reset_token", uuid)
    user.save()
    msg = f"passwod reset token is {uuid}"
    send_email(user.email, "Reset Password", msg)
    return jsonify({"message": "Reset token sent to your email"}), 200


@users_blueprint.route("/users/reset_token", methods=["PUT"], strict_slashes=False)
def reset_password():
    """
    Resets user password
    """
    from uuid import UUID

    data = request.json
    if not data:
        return jsonify({"error": "Not a Json"}), 400
    required = ["password", "token"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} not found"}), 400
    token = data.get("token")
    password = data.get("password")
    password = hash_password(password)
    user = User.objects(reset_token=token).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    setattr(user, "password", password)
    user.save()
    user.update(unset__reset_token=1)
    return jsonify({"Message": "Password changed"}), 200
