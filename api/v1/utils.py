#!/usr/bin/env python3
"""
Module supplies utility functions
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hashes a string password and return bytes representation
    """
    byte_pw = password.encode('utf-8')
    hashed_pw = bcrypt.hashpw(byte_pw, bcrypt.gensalt())
    return hashed_pw
