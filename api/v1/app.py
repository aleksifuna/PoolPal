#!/usr/bin/env python3
"""
Flask application entry module
"""
from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from api.v1.views import app_views

app = Flask(__name__)
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/v1*": {"origins": "*"}})
connect(db='poolpal')


if __name__ == "__main__":
    app.run(debug=True)
