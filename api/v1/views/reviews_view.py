#!/usr/bin/env python3
"""
View for handling sending of reviews API actions
"""
from flask import jsonify, request
from models.user import User
from models.user import Review
from models.ride import Ride
from . import app_views
from bson import ObjectId

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


@app_views.route(
        'rides/<ride_id>/reviews',
        methods=['POST'],
        strict_slashes=False
        )
@jwt_required()
def post_driver_review(ride_id):
    """
    Posts a driver review
    """
    ride = Ride.objects(id=ride_id).first()
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    driver_id = str(ride.driver_id)
    passenger_id = get_jwt_identity()
    if passenger_id not in ride.booked_seats:
        return jsonify({'error': 'Cannot perfom this action'}), 401
    driver = User.objects(id=driver_id).first()
    required = ['rating', 'feedback']
    data = request.json
    if not data:
        return jsonify({'error': 'Not a Json'}), 400
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} missing'}), 400
    review = Review()
    for key, value in data.items():
        setattr(review, key, value)
    setattr(review, 'ride_id', ObjectId(ride_id))
    setattr(review, 'user_id', ObjectId(passenger_id))
    driver.reviews.append(review)
    driver.save()
    return (driver.todict()), 201
