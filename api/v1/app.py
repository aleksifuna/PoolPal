#!/usr/bin/env python3
"""
Flask application entry module
"""
import os
from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from api.v1.views import app_views
from flask_swagger_ui import get_swaggerui_blueprint

load_dotenv()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = 'file_uploads/profile_pic'
    app.config['UPLOAD_EXTENSIONS'] = ['jpg', 'jpeg']
    jwt = JWTManager(app)
    cors = CORS(app, resources={r"/api/v1*": {"origins": "*"}})
    if config_name == 'default':
        db_name = os.getenv('DB_NAME')
    else:
        db_name = 'poolpal_test'

    connect(host=os.getenv('MONGODB_URI'), db=db_name, uuidRepresentation='standard')

    SWAGGER_URL = "/docs"
    API_URL = "/static/swagger.json"
    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "api_name": "Access API"
        }
    )

    app.register_blueprint(app_views)
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
