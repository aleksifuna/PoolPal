#!/usr/bin/env python3
"""
View for handling sending of reviews API actions
"""
from flask import jsonify, request, Blueprint
from api.v2.models.user import User
from api.v2.models.user import Review
from api.v2.models.ride import Ride
from bson import ObjectId

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


reviews_blueprint = Blueprint("reviews", __name__)


@reviews_blueprint.route(
    "rides/<ride_id>/reviews", methods=["POST"], strict_slashes=False
)
@jwt_required()
def post_driver_review(ride_id):
    """
    Posts a driver review
    """
    ride = Ride.objects(id=ride_id).first()
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
    driver_id = str(ride.driver_id)
    passenger_id = get_jwt_identity()
    if passenger_id not in ride.booked_seats:
        return jsonify({"error": "Cannot perfom this action"}), 401
    driver = User.objects(id=driver_id).first()
    required = ["rating", "feedback"]
    data = request.json
    if not data:
        return jsonify({"error": "Not a Json"}), 400
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} missing"}), 400
    review = Review()
    for key, value in data.items():
        setattr(review, key, value)
    setattr(review, "ride_id", ObjectId(ride_id))
    setattr(review, "user_id", ObjectId(passenger_id))
    driver.reviews.append(review)
    driver.save()
    return (driver.todict()), 201


@reviews_blueprint.route(
    "/rides/<ride_id>/reviews/<user_id>", methods=["POST"], strict_slashes=False
)
@jwt_required()
def post_passenger_review(ride_id, user_id):
    """
    Handles posting of pasangers review
    """
    ride = Ride.objects(id=ride_id).first()
    if not ride:
        return jsonify({"error": "Ride not found"})
    if user_id not in ride.booked_seats:
        return jsonify("Cannot perfom this action"), 401
    driver_id = get_jwt_identity()
    passenger = User.objects(id=user_id).first()
    if not passenger:
        return jsonify({"error": "Passenger not found"})
    data = request.json
    required = ["rating", "feedback"]
    for field in data:
        if field not in required:
            return jsonify({"error": "{field} missing"}), 400
    review = Review()
    for key, value in data.items():
        setattr(review, key, value)
    setattr(review, "ride_id", ObjectId(ride_id))
    setattr(review, "user_id", ObjectId(driver_id))
    passenger.reviews.append(review)
    passenger.save()
    return (passenger.todict()), 201
