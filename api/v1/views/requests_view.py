#!/usr/bin/env python3
"""
View for Request object that handles all the RESTFul API action
"""
from flask import jsonify
from models.ride import Ride
from models.ride import Request
from models.user import User
from . import app_views
from datetime import datetime
from bson import ObjectId

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


@app_views.route(
        '/rides/<ride_id>/requests',
        methods=['POST'],
        strict_slashes=False
        )
@jwt_required()
def send_request(ride_id):
    """
    Makes a request to join a ride
    """
    user_id = get_jwt_identity()
    ride = Ride.objects(id=ride_id).first()
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    for request in ride.requests:
        if ObjectId(user_id) == request.user_id:
            Ride.objects(
                id=ride_id, requests__user_id=ObjectId(user_id)
                ).update_one(set__requests__S__status='pending')
            ride.update_at = datetime.now()
            ride.save()
            ride.reload()
            return jsonify(ride.todict()), 200
    req = Request()
    setattr(req, 'user_id', user_id)
    ride.requests.append(req)
    ride.save()
    # send email to driver to approve
    return jsonify(ride.todict()), 201


@app_views.route(
        '/rides/<ride_id>/requests',
        methods=['PUT'],
        strict_slashes=False
        )
@jwt_required()
def cancel_request(ride_id):
    """
    Cancels a request to join ride
    """
    user_id = get_jwt_identity()
    ride = Ride.objects(id=ride_id).first()
    if user_id in ride.booked_seats:
        ride.remove_booking(user_id)
        # add users cancelled trips
        # send email notification to driver
    Ride.objects(
        id=ride.id, requests__user_id=ObjectId(user_id)
        ).update_one(set__requests__S__status='canceled')
    ride.update_at = datetime.now()
    ride.save()
    ride.reload()
    return jsonify(ride.todict()), 200


@app_views.route('/requests', methods=['GET'], strict_slashes=False)
@jwt_required()
def passenger_requests():
    """
    Queries and returns all requests sent by a passenger
    """
    user_id = get_jwt_identity()
    rides = Ride.objects(requests__user_id=user_id)
    requests_list = [ride.todict() for ride in rides]
    return jsonify(requests_list)


@app_views.route('/requests/<user_id>', methods=['POST'], strict_slashes=False)
@jwt_required()
def accept_request(user_id):
    """
    Accepts passagers request to join ride
    """
    driver_id = get_jwt_identity()
    user = User.objects(id=driver_id).first()
    if user.role == 'passenger':
        return jsonify({'error': 'Action can only be perfomed by driver'}), 401
    ride = Ride.objects(requests__user_id=user_id).first()
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    Ride.objects(
        id=ride.id, requests__user_id=ObjectId(user_id)
        ).update_one(set__requests__S__status='approved')
    ride.update_at = datetime.now()
    ride.save()
    ride.add_booking(user_id)
    ride.reload()
    # send email to passanger with driver details
    return jsonify(ride.todict()), 200
