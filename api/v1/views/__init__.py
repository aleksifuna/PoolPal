#!/usr/bin/env python3
"""
Blueprint views setup module
"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')

from . import users_view
from . import rides_view
from . import requests_view
from . import reviews_view
from . import files_view
