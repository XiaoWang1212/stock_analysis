from flask import Flask
from flask_cors import CORS
from covid_app import covid_app_blueprint
from stock_app import stock_app_blueprint

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Welcome to the Flask app! Use /covid_app/api/data or /stock_app/api/data for specific routes."

# 註冊 Blueprint
app.register_blueprint(covid_app_blueprint, url_prefix='/covid_app')  
app.register_blueprint(stock_app_blueprint, url_prefix='/stock_app')  

if __name__ == '__main__':
    app.run(debug=True)
