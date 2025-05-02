#!/usr/bin/env python3
"""
view for Ride object that handles all the RESTFul API actions
"""
from flask import jsonify, request
from models.user import User
from models.ride import Ride
from . import app_views
from api.v1.utils import get_distance
from datetime import datetime
from bson import ObjectId
import re

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required


@app_views.route('/rides', methods=['POST'], strict_slashes=False)
@jwt_required()
def add_ride():
    """
    Creates a ride
    """
    user_id = get_jwt_identity()
    required = [
        'origin',
        'destination',
        'date_time',
        'available_seats'
        ]
    data = request.json
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} Missing'}), 400
    user = User.objects(id=user_id).first()
    if user.role == 'passenger':
        return jsonify({'error': 'Only drivers can perfom this action'}), 401
    ride = Ride()
    for key, value in data.items():
        if key not in required:
            return jsonify({'error': f'Cannot set {key}'}), 401
        if key == 'date_time':
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        setattr(ride, key, value)
    distance = get_distance(data.get('origin'), data.get('destination'))
    if distance.get('status') != 'Found':
        response = {}
        if distance.get('message_1'):
            response['destination_error'] = distance.get('message_1')
        if distance.get('message_2'):
            response['origin_error'] = distance.get['message_2']
        return jsonify(response), 404
    ride.distance = distance.get('distance')
    ride.offer_trip_fee = ride.chargeable_fare()
    ride.driver_id = ObjectId(user_id)
    ride.save()
    return jsonify(ride.todict()), 201


@app_views.route('/rides/<ride_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_ride(ride_id):
    """
    Return the details of a specific Ride with ride_id
    """
    driver_id = get_jwt_identity()
    ride = Ride.objects(id=ride_id).first()
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    if ride.driver_id != ObjectId(driver_id):
        return jsonify({'error': 'Not authorized'}), 401
    return jsonify(ride.todict()), 200


@app_views.route('/rides/<ride_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_ride(ride_id):
    """
    Updates the ride details
    """
    updateable = [
        'origin',
        'destination',
        'distance',
        'date_time',
        'available_seats'
        ]
    driver_id = get_jwt_identity()
    ride = Ride.objects(id=ride_id).first()
    if not ride:
        return jsonify({'error': 'Ride not found'}), 404
    if ride.driver_id != ObjectId(driver_id):
        return jsonify({'error': 'Not authorized'}), 401
    data = request.json
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    for key, value in data.items():
        if key not in updateable:
            return jsonify({'error': f'Cannot edit {key}'}), 400
        if key == 'date_time':
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        setattr(ride, key, value)
    ride.updated_at = datetime.now()
    ride.save()
    return jsonify(ride.todict()), 200


@app_views.route('/rides/trips', methods=['POST'], strict_slashes=False)
def search_rides():
    """
    Searches and returns rides
    """
    data = request.json
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    required = ['origin', 'destination', 'date_time']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} Missing'}), 400
    origin = data.get('origin')
    destination = data.get('destination')
    date_time = datetime.strptime(data.get('date_time'), '%Y-%m-%dT%H:%M:%S')
    origin_regex = re.compile(re.escape(origin), re.IGNORECASE)
    destination_regex = re.compile(re.escape(destination), re.IGNORECASE)
    rides = Ride.objects(
        origin=origin_regex,
        destination=destination_regex,
        date_time__gte=date_time
    )
    rides_dicts = [ride.todict() for ride in rides]
    return jsonify(rides_dicts), 200
