#!/usr/bin/env/ python3
"""
Webapp factory
"""
from api.config import DevelopmentConfig, TestingConfig, ProductionConfig
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate


load_dotenv
db = SQLAlchemy()


def create_app(environment: str) -> Flask:
    """
    Creates a Flask application instance
    """
    app = Flask(__name__)
    if environment == 'development':
        app.config.from_object(DevelopmentConfig)
    elif environment == 'testing':
        app.config.from_object(TestingConfig)
    elif environment == 'production':
        app.config.from_object(ProductionConfig)
    CORS(app, supports_credentials=True, resources={"/*": {"origins": "*"}})
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    with app.app_context():
        from models import ride, user
