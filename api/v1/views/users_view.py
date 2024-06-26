#!/usr/bin/env python3
"""
View for User object that handles all RESTFul API actions
"""
from flask import jsonify, request
from models.user import User
from models.user import DriverDetails
from api.v1.utils import hash_password
from . import app_views
from datetime import datetime
import bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def register_user():
    """
    Registers a user
    """
    if not request.json:
        return jsonify({'error': 'Not a JSON'}), 400
    data = request.json
    required = ['first_name', 'email', 'phone', 'password']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400
    if User.objects(email=data['email']).first():
        return jsonify({'error': 'User already Exists'}), 400
    data['password'] = hash_password(data['password'])
    user = User()
    for key, value in data.items():
        setattr(user, key, value)
    user.save()
    return jsonify(user.todict()), 201


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def get_user(user_id):
    """
    Returns the details of a user
    """
    user = User.objects(id=user_id).first()
    if user:
        return jsonify(user.todict()), 200
    return jsonify({'error': 'Not Found'}), 404


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
@jwt_required
def update_user(user_id):
    """
    Updates the details of the user
    """
    identity = get_jwt_identity()
    if user_id != identity:
        return jsonify({
            'error': 'unauthorized'
            }), 401
    editable = [
        'first_name',
        'last_name',
        'phone',
        'preferences',
        'profile_picture',
        'role'
        ]
    data = request.json
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'error': 'Not Found'}), 404
    for key, value in data.items():
        if key not in editable:
            return jsonify({'error': f'{key} cant be changed'}), 400
        setattr(user, key, value)
    user.updated_at = datetime.now()
    user.save()
    return jsonify(user.todict()), 200


@app_views.route(
        '/users/<user_id>/driver',
        methods=['POST'],
        strict_slashes=False
        )
@jwt_required()
def add_driver_details(user_id):
    identity = get_jwt_identity()
    if user_id != identity:
        return jsonify({
            'error': 'unauthorized'
        }), 401
    data = request.json
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    required = ['car_model', 'car_number_plate', 'license_number']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} missing'}), 400
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'error': 'User Not Found'}), 404
    if user.role == 'passenger':
        return jsonify({
            'error': 'Action can only be perfomed by drivers'
            }), 401
    if user.driver_details:
        return jsonify({'error': 'Driver details already set'}), 400
    driver_dets = DriverDetails()
    for key, value in data.items():
        setattr(driver_dets, key, value)
    setattr(user, 'driver_details', driver_dets)
    user.save()
    return jsonify(user.todict()), 201


@app_views.route(
        '/users/<user_id>/driver',
        methods=['PUT'],
        strict_slashes=False
        )
@jwt_required()
def update_driver_details(user_id):
    identity = get_jwt_identity()
    if user_id != identity:
        return jsonify({
            'error': 'unauthorized'
        }), 401
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'error': 'User Not Found'}), 404
    if user.role == 'passenger':
        return jsonify({
            'error': 'Action can only be perfomed by drivers'
            }), 401
    if not user.driver_details:
        return jsonify({'error': 'No driver details set'}), 400
    data = request.json
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    required = ['car_model', 'car_number_plate', 'license_number']
    update_dict = {}
    for key, value in data.items():
        if key not in required:
            return jsonify({'error': f'Cannot update {key}'}), 400
        update_dict[f'set__driver_details__{key}'] = value
    user.update(**update_dict)
    user.updated_at = datetime.now()
    user.save()
    user.reload()
    return jsonify(user.todict()), 200


@app_views.route('/users/login', methods=['POST'], strict_slashes=False)
def user_login():
    """
    Logins in the user session
    """
    data = request.json
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    required = ['email', 'password']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is missing'}), 400
    user = User.objects(email=data['email']).first()
    if not user:
        return jsonify({'error': 'User Not Found'}), 404
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password):
        return jsonify({'error': 'Wrong Email or Password'}), 400
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)
