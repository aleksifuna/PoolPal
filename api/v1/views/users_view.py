#!/usr/bin/env python3
"""
View for User object that handles all RESTFul API actions
"""
from flask import jsonify, request
from models.user import User
from api.v1.utils import hash_password
from . import app_views
from datetime import datetime


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
def update_user(user_id):
    """
    Updates the details of the user
    """
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
