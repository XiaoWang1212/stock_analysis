from . import covid_app_blueprint
from flask import jsonify

@covid_app_blueprint.route('/api/data', methods=['GET'])
def get_first_app_data():
    return jsonify({"message": "Hello from the first app!"})