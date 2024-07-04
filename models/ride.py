#!/usr/bin/env python3
"""
Ride model module
"""
import mongoengine
import os
from bson import ObjectId
from datetime import datetime


class Request(mongoengine.EmbeddedDocument):
    """
    Request model class attributes and methods defination
    """
    user_id = mongoengine.ObjectIdField(required=True)
    status = mongoengine.StringField(default='pending')

    def to_dict(self):
        """
        Returns a dictionary representation of the object
        """
        return {
            'user_id': str(self.user_id),
            'status': self.status
        }


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
    requests = mongoengine.EmbeddedDocumentListField(Request)
    offer_trip_fee = mongoengine.FloatField(required=True)
    trip_fee = mongoengine.FloatField(require=True)
    reviewed = mongoengine.BooleanField(default=False)
    status = mongoengine.StringField(default='pending')
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
        Adds a user to a ride and adjusts the max chargeable fare
        """
        self.booked_seats.append(user_id)
        passangers = len(self.booked_seats) + 1
        self.offer_trip_fee = self.chargeable_fare() / passangers
        self.available_seats -= 1
        if passangers == 1:
            self.trip_fee = self.chargeable_fare()
        else:
            self.trip_fee = self.chargeable_fare() / passangers - 1
        self.save()

    def remove_booking(self, user_id):
        """
        Removes a users from a ride and adjusts the max chargeable fare
        """
        self.booked_seats.remove(user_id)
        passangers = len(self.booked_seats) + 1
        self.offer_trip_fee = self.chargeable_fare() / passangers
        self.available_seats += 1
        if passangers == 1:
            self.trip_fee = self.chargeable_fare()
        else:
            self.trip_fee = self.chargeable_fare() / passangers - 1
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
            elif isinstance(value, mongoengine.EmbeddedDocument):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [
                    v.to_dict() if isinstance(
                        v, mongoengine.EmbeddedDocument
                        ) else v for v in value
                    ]
            obj_dict[field] = value
        return obj_dict

    meta = {
        'collection': 'rides',
        'indexes': ['origin', 'destination', 'date_time']
    }
