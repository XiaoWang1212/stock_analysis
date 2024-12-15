from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask import jsonify, request
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8080"],  # Vue.js 開發伺服器的位置
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config["MONGO_URI"] = "mongodb://localhost:27017/stock"
app.config["SECRET_KEY"] = "secret_key"
mongo = PyMongo(app)

@app.route('/')
def index():
    return "Welcome to the Flask app! Use /stock_app/api/data for specific routes."

@app.route("/register", methods=["POST"])
def register():
    users = mongo.db.users
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    # 檢查用戶是否已存在
    if users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400
        
    # 創建新用戶
    hashed_password = generate_password_hash(password)
    user_id = users.insert_one({
        "email": email,
        "password": hashed_password,
        "groups": [{"name": f"Group {i+1}", "stocks": []} for i in range(6)]  # 預設六個空群組
    }).inserted_id
    
    return jsonify({"message": "User created successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    users = mongo.db.users
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = users.find_one({"email": email})
    
    if not user:
        return jsonify({"error": "Account not found"}), 404
    
    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Incorrect password"}), 401
    
    # 確保用戶資料包含 groups 欄位
    if "groups" not in user:
        user["groups"] = [{"name": f"Group {i+1}", "stocks": []} for i in range(6)]
        users.update_one({"_id": user["_id"]}, {"$set": {"groups": user["groups"]}})
        
    current_time = datetime.datetime.utcnow()
    token = jwt.encode({
        "user_id": str(user["_id"]),
        "email": user["email"],
        "iat": current_time,  # 令牌簽發時間
        "exp": current_time + datetime.timedelta(days=1),  # 延長到 1 天
        "nbf": current_time  # 令牌生效時間
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({
        "message": "Login successful", 
        "token": token,
        "userId": str(user["_id"]),
        "email": user["email"],
        "expiresIn": 86400  # 1天的秒數，方便前端處理過期時間
    }), 200

@app.route("/groups/<user_id>", methods=["GET"])
def get_groups(user_id):
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": "Invalid user ID format"}), 400
        
    user = mongo.db.users.find_one({"_id": object_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"groups": user["groups"]}), 200

@app.route("/groups/<user_id>", methods=["POST"])
def update_groups(user_id):
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": "Invalid user ID format"}), 400
        
    data = request.get_json()
    group_index = data.get("index")
    group_name = data.get("name")
    stocks = data.get("stocks")
    
    update = {}
    if group_name:
        update[f"groups.{group_index}.name"] = group_name
    if stocks is not None:
        update[f"groups.{group_index}.stocks"] = stocks
    
    result = mongo.db.users.update_one(
        {"_id": object_id},
        {"$set": update}
    )
    
    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"message": "Group updated successfully"}), 200
    
# 註冊 Blueprint
from stock_app import stock_app_blueprint
app.register_blueprint(stock_app_blueprint, url_prefix='/stock_app')  

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
