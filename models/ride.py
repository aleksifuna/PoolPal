#!/usr/bin/env python3
"""
Ride model module
"""
import mongoengine
import os
from bson import ObjectId
from datetime import datetime


class Ride(mongoengine.Document):
    """
    Ride model class attributes and methods defination
    """
    driver_id = mongoengine.ObjectIdField(required=True)
    origin = mongoengine.StringField(required=True)
    destination = mongoengine.StringField(required=True)
    distance = mongoengine.FloatField(required=True)
    date_time = mongoengine.DateTimeField(required=True)
    available_seats = mongoengine.IntField(required=True)
    booked_seats = mongoengine.ListField()
    max_chargeable_fare = mongoengine.FloatField(required=True)
    reviewed = mongoengine.BooleanField(default=False)
    updated_at = mongoengine.DateTimeField()

    def chargeable_fare(self):
        """
        Calculates the fare to be charged based on the distance
        """
        fuel_consumption = 10
        fuel_consumed = self.distance / fuel_consumption
        fuel_price = float(os.getenv('FUEL_PRICE'))
        trip_fuel_cost = fuel_consumed * fuel_price
        maintenance_insurance = 0.10 * trip_fuel_cost
        total_cost = trip_fuel_cost + maintenance_insurance
        drivers_contribution = 0.20 * total_cost
        passenger_contribution = total_cost - drivers_contribution
        return passenger_contribution

    def add_booking(self, user_id):
        """
        Adds a user to a ride and adjusts the max chargable fare
        """
        self.booked_seats.append(user_id)
        passangers = len(self.booked_seats) + 1
        self.max_chargeable_fare = self.chargeable_fare / passangers
        self.save()

    def todict(self):
        """
        Returns a dictinary representation of the objects attributes
        """
        obj_dict = {}
        for field in self._fields.keys():
            value = getattr(self, field)
            if isinstance(value, ObjectId):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            obj_dict[field] = value
        return obj_dict

    meta = {
        'collection': 'rides',
        'indexes': ['origin', 'destination', 'date_time']
    }
