#!/usr/bin/env python3
"""
Module supplies utility functions
"""
import bcrypt
import googlemaps
import os
from mailjet_rest import Client
import uuid


def hash_password(password: str) -> bytes:
    """
    Hashes a string password and return bytes representation
    """
    byte_pw = password.encode('utf-8')
    hashed_pw = bcrypt.hashpw(byte_pw, bcrypt.gensalt())
    return hashed_pw


def get_distance(origin: str, destination: str) -> dict:
    """
    Gets the distance between origin and destination in km
    """
    KEY = os.getenv('GOOGLE_KEY')
    result = {}
    gmaps = googlemaps.Client(key=KEY)
    matrix = gmaps.distance_matrix(origin, destination)
    status = matrix.get('rows')[0].get('elements')[0].get('status')
    if status == 'NOT_FOUND':
        result['status'] = 'not found'
        if '' in matrix.get('destination_addresses'):
            result['message_1'] = 'Destination Not Found! Try Again!'
        elif '' in matrix.get('origin_addresses'):
            result['message_2'] = 'Origin Not Found! Try Again!'
        return result
    result = matrix.get('rows')[0].get('elements')[0]
    distance = result.get('distance').get('text')
    distance = float(distance.split(' ')[0])
    result['distance'] = distance
    result['status'] = 'Found'
    return(result)


def send_email(email: str, subject: str, msg: str) -> bool:
    api_key = os.environ['MJ_KEY']
    api_secret = os.environ['MJ_SECRET']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "aleksifuna@gmail.com",
                    "Name": "poolpal"
                    },
                "To": [
                    {
                        "Email": email,
                        "Name": "You"
                    }
                ],
                "Subject": subject,
                "TextPart": msg
            }
        ]
    }
    result = mailjet.send.create(data=data)
    if result.status_code == 200:
        return True
    return False


def generate_uuid() -> str:
    """
    Generate a UUID code then returns it
    """
    return str(uuid.uuid4())
