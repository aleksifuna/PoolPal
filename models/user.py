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


class User(mongoengine.Document):
    """
    User model class attributes and methods defination
    """
    first_name = mongoengine.StringField(required=True)
    last_name = mongoengine.StringField()
    email = mongoengine.EmailField(required=True, unique=True)
    phone = mongoengine.StringField(required=True)
    password = mongoengine.BinaryField(required=True)
    profile_picture = mongoengine.URLField()
    preferences = mongoengine.DictField()
    role = mongoengine.StringField(default='passenger')
    driver_details = mongoengine.EmbeddedDocumentField(DriverDetails)
    reset_token = mongoengine.UUIDField()
    account_verified = mongoengine.BooleanField(default=False)
    created_at = mongoengine.DateTimeField(default=datetime.now)
    updated_at = mongoengine.DateTimeField()

    def todict(self):
        """
        Returns a dictionary representation of object attributes
        """
        skip_fields = ['password', 'reset_token']
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
            obj_dict[field_name] = value
        if self.role == 'passenger':
            del obj_dict['driver_details']
        return obj_dict

    meta = {
        'collection': 'users',
        'indexes': ['email']
    }
