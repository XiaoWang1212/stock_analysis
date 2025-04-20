from flask import Blueprint
from flask_cors import CORS # type: ignore

stock_app_blueprint = Blueprint('stock_app', __name__)

CORS(stock_app_blueprint, resources={
    r"/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

from . import routes
from . import stockTW