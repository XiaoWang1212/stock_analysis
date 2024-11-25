from flask import Blueprint

covid_app_blueprint = Blueprint('covid_app', __name__)

from . import routes