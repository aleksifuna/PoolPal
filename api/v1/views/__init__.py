#!/usr/bin/env python3
"""
Blueprint views setup module
"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')

from . import users_view
