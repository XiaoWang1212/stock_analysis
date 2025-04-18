from flask import Blueprint

stock_app_blueprint = Blueprint('stock_app', __name__)

from . import routes
from . import stockTW