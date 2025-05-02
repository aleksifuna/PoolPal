#!/usr/bin/env/ python3
"""
Webapp factory
"""
from api.config import DevelopmentConfig, TestingConfig, ProductionConfig
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from mongoengine import connect
from flask_swagger_ui import get_swaggerui_blueprint
import os

load_dotenv()


def create_app(environment: str) -> Flask:
    """
    Creates and returns a Flask application instance
    """
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    static_path = os.path.join(basedir, "api", "static")
    app = Flask(__name__, static_folder=static_path, static_url_path="/static")
    if environment == "development":
        app.config.from_object(DevelopmentConfig)
    elif environment == "testing":
        app.config.from_object(TestingConfig)
    elif environment == "production":
        app.config.from_object(ProductionConfig)

    JWTManager(app)
    CORS(app, supports_credentials=True, resources={"/*": {"origins": "*"}})

    SWAGGER_URL = "/docs"
    API_URL = "/static/swagger.json"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Ride Sharing API"}
    )

    connect(
        db=app.config["MONGODB_DB"],
        host=app.config["MONGODB_HOST"],
        port=int(app.config["MONGODB_PORT"]),
        username=app.config["MONGODB_USERNAME"],
        password=app.config["MONGODB_PASSWORD"],
        uuidRepresentation="standard",
    )
    with app.app_context():
        from .users_view import users_blueprint
        from .rides_view import rides_blueprint
        from .requests_view import requests_blueprint
        from .files_view import files_blueprint
        from .requests_view import requests_blueprint

        app.register_blueprint(users_blueprint, url_prefix="/api/v2")
        app.register_blueprint(rides_blueprint, url_prefix="/api/v2")
        app.register_blueprint(requests_blueprint, url_prefix="/api/v2")
        app.register_blueprint(files_blueprint, url_prefix="/api/v2")
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
