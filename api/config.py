#!/usr/bin/env python3
"""
contains configurations for the webapp
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Base configuration class
    """
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    SQLALCEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """
    Development configuration class
    """
    DEBUG = True


class TestingConfig(Config):
    """
    Testing configuration class
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL')
    DEBUG = True


class ProductionConfig(Config):
    """
    Production configuration class
    """
    DEBUG = False
