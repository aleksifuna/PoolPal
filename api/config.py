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

    SECRET_KEY = os.getenv("APP_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO = False
    SQLALCEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS")
    JWT_REFRESH_TOKEN_EXPIRES_DAYS = os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS")
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE")
    JWT_TOKEN_LOCATION = os.getenv("JWT_TOKEN_LOCATION")
    JWT_COOKIE_CSRF_PROTECT = os.getenv("JWT_COOKIE_CSRF_PROTECT")

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    UPLOAD_EXTENSIONS = os.getenv("UPLOAD_EXTENSIONS")
    MONGODB_HOST = os.getenv("MONGO_URI")
    MONGODB_PORT = os.getenv("MONGO_PORT")
    MONGODB_USERNAME = os.getenv("MONGO_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGODB_DB = os.getenv("MONGO_DB")


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
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
    DEBUG = True


class ProductionConfig(Config):
    """
    Production configuration class
    """

    DEBUG = False
