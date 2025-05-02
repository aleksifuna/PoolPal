#!/usr/bin/env python3
"""
User model module
"""

import mongoengine
from datetime import datetime
from bson import ObjectId


class DriverDetails(mongoengine.EmbeddedDocument):
    """
    Defines the attributes for a drivers details
    """
    car_model = mongoengine.StringField(required=True)
    car_number_plate = mongoengine.StringField(required=True)
    license_number = mongoengine.StringField(required=True)

    def to_dict(self):
        """
        Returns a dictionary representation of the driver details
        """
        return {
            "car_model": self.car_model,
            "car_number_plate": self.car_number_plate,
            "license_number": self.license_number
        }


class Review(mongoengine.EmbeddedDocument):
    """
    Defines a review class attribute and methods
    """
    ride_id = mongoengine.ObjectIdField(required=True)
    user_id = mongoengine.ObjectIdField(required=True)
    rating = mongoengine.IntField(required=True)
    feedback = mongoengine.StringField()

    def to_dict(self):
        """
        Returns a dictionary representation of the instance
        """
        return {
            "ride_id": str(self.ride_id),
            "user_id": str(self.user_id),
            "rating": self.rating,
            "feedback": self.feedback
        }


class User(mongoengine.Document):
    """
    User model class attributes and methods defination
    """
    first_name = mongoengine.StringField(required=True)
    last_name = mongoengine.StringField()
    email = mongoengine.EmailField(required=True, unique=True)
    phone = mongoengine.StringField(required=True)
    password = mongoengine.BinaryField(required=True)
    profile_picture = mongoengine.StringField()
    preferences = mongoengine.DictField()
    role = mongoengine.StringField(default='passenger')
    driver_details = mongoengine.EmbeddedDocumentField(DriverDetails)
    reviews = mongoengine.EmbeddedDocumentListField(Review)
    reset_token = mongoengine.UUIDField(binary=False)
    account_verified = mongoengine.BooleanField(default=False)
    created_at = mongoengine.DateTimeField(default=datetime.now)
    updated_at = mongoengine.DateTimeField()
    confirmation_token = mongoengine.UUIDField(binary=False)

    def todict(self):
        """
        Returns a dictionary representation of object attributes
        """
        skip_fields = ['password', 'reset_token', 'confirmation_token']
        obj_dict = {}
        for field_name in self._fields.keys():
            if field_name in skip_fields:
                continue
            value = getattr(self, field_name)
            if isinstance(value, ObjectId):
                value = str(value)
            elif isinstance(value, mongoengine.EmbeddedDocument):
                value = value.to_dict()
            elif isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, list):
                value = [
                    v.to_dict() if isinstance(
                        v, mongoengine.EmbeddedDocument
                        ) else v for v in value
                        ]
            obj_dict[field_name] = value
        if self.role == 'passenger':
            del obj_dict['driver_details']

        return obj_dict

    meta = {
        'collection': 'users',
        'indexes': ['email']
    }
