#!/usr/bin/env python3
"""
Module supplies routes that handle file updloads
"""
import os
from werkzeug.utils import secure_filename
from models.user import User
from flask import send_from_directory, jsonify, request, current_app, Blueprint
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


file_blueprint = Blueprint('files', __name__)


def allowed_file(filename):
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in current_app.config['UPLOAD_EXTENSIONS']:
            return True
    return False


@file_blueprint.route('/users/profile_pic', methods=['POST'], strict_slashes=False)
@jwt_required()
def profile_pic_upload():
    """
    Handles uploading of user's profile picture
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    profile_pic = request.files['file']
    if profile_pic.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(profile_pic.filename)
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type'})
    file_ext = os.path.splitext(filename)[1]
    filename = f'{get_jwt_identity()}{file_ext}'
    profile_pic.save(
        os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    )
    user = User.objects(id=get_jwt_identity()).first()
    setattr(user, 'profile_picture', filename)
    user.save()
    return jsonify({'Status': 'Success'}), 201


@file_blueprint.route(
    '/users/profile_pic/<file_name>',
    methods=['GET'],
    strict_slashes=False
)
def get_profile_pic(file_name):
    """
    Returns the profile picture of user based on filename
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    absolute_path = os.path.abspath(upload_folder)
    print(absolute_path)
    print(file_name)
    return send_from_directory(upload_folder, file_name)
