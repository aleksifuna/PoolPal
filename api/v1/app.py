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

load_dotenv()
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)
cors = CORS(app, resources={r"/api/v1*": {"origins": "*"}})
connect(db='poolpal')
app.register_blueprint(app_views)

if __name__ == "__main__":
    app.run(debug=True)
