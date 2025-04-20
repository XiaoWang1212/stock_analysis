import os
import warnings
import sys
from absl import logging as absl_logging # type: ignore

# 完全抑制 absl 警告
absl_logging.set_verbosity(absl_logging.ERROR)

# 隱藏 TensorFlow 的警告
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  

import tensorflow as tf # type: ignore

# 隱藏 TensorFlow 的警告
tf.get_logger().setLevel('ERROR')
warnings.filterwarnings('ignore')

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model, load_model, save_model # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input # type: ignore
import yfinance as yf # type: ignore
import numpy as np
import pandas as pd
from flask import jsonify, request
from datetime import datetime, timedelta
import pickle

from . import stock_app_blueprint

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(symbol):
    return os.path.join(MODEL_DIR, f"{symbol}_lstm_model.keras")

def get_scaler_path(symbol):
    return os.path.join(MODEL_DIR, f"{symbol}_scaler.pkl")

def create_lstm_model(input_shape):
    inputs = Input(shape=input_shape)
    x = LSTM(units=50, return_sequences=True)(inputs)
    x = Dropout(0.2)(x)
    x = LSTM(units=50)(x)
    x = Dropout(0.2)(x)
    outputs = Dense(units=1)(x)
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', 
                  loss='mean_squared_error', 
                  metrics=['mean_absolute_error']
            )
    return model

def generate_future_dates(start_date, days=7):
    """生成指定天數的未來交易日期（跳過週末）"""
    future_dates = []
    current_date = start_date
    
    for _ in range(days):
        # 前進到下一天
        current_date = current_date + timedelta(days=1)
        
        # 跳過週末
        while current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            current_date = current_date + timedelta(days=1)
        
        future_dates.append(current_date.strftime('%Y-%m-%d'))
    
    return future_dates

@stock_app_blueprint.route('/api/lstm_predict/<symbol>', methods=['GET'])
def lstm_predict_stock(symbol):
    try:
        model_path = get_model_path(symbol)
        scaler_path = get_scaler_path(symbol)
        prediction_days = 60  # 預測窗口大小，與訓練時一致
        
        # 檢查是否需要重新訓練模型
        force_retrain = request.args.get('retrain', 'false').lower() == 'true'
        
        if os.path.exists(model_path) and os.path.exists(scaler_path) and not force_retrain:
            # 載入現有模型
            model = load_model(model_path)
            
            # 初始化模型度量
            dummy_x = np.zeros((1, prediction_days, 1))
            dummy_y = np.zeros((1,))
            # 靜默評估
            model.evaluate(dummy_x, dummy_y, verbose=0)

            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
                
            # 只獲取近期數據用於預測
            stock = yf.Ticker(symbol)
            recent_data = stock.history(period="3mo")
            
            if recent_data.empty:
                return jsonify({"error": f"No recent data found for symbol: {symbol}"}), 404
            
            # 準備預測數據
            prices = recent_data['Close'].values.reshape(-1, 1)
            scaled_prices = scaler.transform(prices)
            
            # 確保有足夠的數據
            if len(scaled_prices) < prediction_days:
                return jsonify({"error": f"Insufficient data for prediction (need at least {prediction_days} data points)"}), 400
            
            # 準備測試數據
            x_test = []
            for i in range(prediction_days, len(scaled_prices)):
                x_test.append(scaled_prices[i-prediction_days:i, 0])
            
            if len(x_test) == 0:
                return jsonify({"error": f"Cannot create prediction sequences from available data"}), 400
            
            x_test = np.array(x_test)
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
            
            # 進行預測
            predicted_prices = model.predict(x_test, verbose=0)
            predicted_prices = scaler.inverse_transform(predicted_prices)
            
            # 計算未來日期
            last_date = recent_data.index[-1]
            future_dates = generate_future_dates(last_date)
            
            # 預測未來 7 天
            future_predictions = []
            last_sequence = scaled_prices[-prediction_days:].reshape(1, prediction_days, 1)
            
            for _ in range(7):
                # 預測下一天
                next_day = model.predict(last_sequence, verbose=0)[0]
                future_predictions.append(next_day[0])
                
                # 更新序列
                new_sequence = np.copy(last_sequence)
                new_sequence = new_sequence[:, 1:, :]
                new_sequence = np.append(new_sequence, [[[next_day[0]]]], axis=1)
                last_sequence = new_sequence
            
            # 將預測結果轉回實際價格
            future_prices = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
            
            # 計算預測準確性
            if len(x_test) > 0:
                actual_prices = recent_data['Close'][-len(predicted_prices):].values
                mse = np.mean((actual_prices - predicted_prices.flatten())**2)
                rmse = np.sqrt(mse)
                accuracy = max(0, 100 - min(100, (rmse / np.mean(actual_prices)) * 100))
            else:
                accuracy = 0
                rmse = 0
            
            # 計算價格變化百分比
            current_price = float(recent_data['Close'].iloc[-1])
            next_price = float(future_prices[0][0])
            price_change = ((next_price - current_price) / current_price) * 100
            
            # 計算歷史資料以供圖表使用
            historical_dates = recent_data.index[-30:].strftime('%Y-%m-%d').tolist()
            historical_prices = recent_data['Close'][-30:].tolist()
            
            # 整理響應數據
            response = {
                "symbol": symbol,
                "current_price": current_price,
                "predicted_next_price": next_price,
                "price_change_percent": float(price_change),
                "prediction_accuracy": float(accuracy),
                "rmse": float(rmse),
                "signal": "買入" if price_change > 0 else "賣出",
                "historical_data": {
                    "dates": historical_dates,
                    "prices": [float(p) for p in historical_prices]
                },
                "future_predictions": [
                    {"date": date, "price": round(float(price[0]), 2)} 
                    for date, price in zip(future_dates, future_prices)
                ],
                "model_info": {
                    "last_updated": datetime.fromtimestamp(os.path.getmtime(model_path)).strftime('%Y-%m-%d'),
                    "prediction_days": prediction_days
                }
            }
            
            return jsonify(response)
            
        else:
            # 訓練新模型
            stock = yf.Ticker(symbol)
            data = stock.history(period="1y")

            if data.empty:
                return jsonify({"error": f"No data found for symbol: {symbol}"}), 404
            
            data['Close'] = data['Close'].astype(float)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

            # training data
            x_train, y_train = [], []

            for x in range(prediction_days, len(scaled_data)):
                x_train.append(scaled_data[x-prediction_days:x, 0])
                y_train.append(scaled_data[x, 0])

            x_train, y_train = np.array(x_train), np.array(y_train)
            x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

            # 使用改進的 LSTM 模型
            input_shape = (x_train.shape[1], 1)
            model = create_lstm_model(input_shape)

            model.fit(x_train, y_train, epochs=25, batch_size=32, verbose=0)

            # 保存模型和縮放器
            model.save(model_path)
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)

            # testing data
            test_data = stock.history(period="1mo")
            total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)
            model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
            model_inputs = model_inputs.reshape(-1, 1)
            model_inputs = scaler.transform(model_inputs)

            x_test = []
            for x in range(prediction_days, len(model_inputs)):
                x_test.append(model_inputs[x-prediction_days:x, 0])

            x_test = np.array(x_test)
            x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

            # 預測
            predicted_prices = model.predict(x_test, verbose=0)
            predicted_prices = scaler.inverse_transform(predicted_prices)
            
            # 預測未來 7 天
            future_predictions = []
            last_sequence = model_inputs[-prediction_days:].reshape(1, prediction_days, 1)
            
            for _ in range(7):
                # 預測下一天
                next_day = model.predict(last_sequence, verbose=0)[0]
                future_predictions.append(next_day[0])
                
                # 更新序列
                new_sequence = np.copy(last_sequence)
                new_sequence = new_sequence[:, 1:, :]
                new_sequence = np.append(new_sequence, [[[next_day[0]]]], axis=1)
                last_sequence = new_sequence
            
            # 將預測結果轉回實際價格
            future_prices = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
            
            # 計算未來日期
            last_date = test_data.index[-1] if not test_data.empty else data.index[-1]
            future_dates = generate_future_dates(last_date)
            
            # 計算預測準確性 (使用測試數據中的實際值與預測值比較)
            if len(test_data) > 0 and len(predicted_prices) > 0:
                actual_prices = test_data['Close'][-len(predicted_prices):].values
                mse = np.mean((actual_prices - predicted_prices.flatten())**2)
                rmse = np.sqrt(mse)
                accuracy = max(0, 100 - min(100, (rmse / np.mean(actual_prices)) * 100))
            else:
                accuracy = 0
                rmse = 0
            
            # 計算價格變化百分比
            current_price = float(test_data['Close'].iloc[-1] if not test_data.empty else data['Close'].iloc[-1])
            next_price = float(future_prices[0][0])
            price_change = ((next_price - current_price) / current_price) * 100
            
            # 計算歷史資料以供圖表使用
            historical_dates = data.index[-30:].strftime('%Y-%m-%d').tolist()
            historical_prices = data['Close'][-30:].tolist()
            
            # 整理響應數據 (明確轉換所有 NumPy 類型)
            response = {
                "symbol": symbol,
                "current_price": current_price,
                "predicted_next_price": next_price,
                "price_change_percent": float(price_change),
                "prediction_accuracy": float(accuracy),
                "rmse": float(rmse),
                "signal": "買入" if price_change > 0 else "賣出",
                "historical_data": {
                    "dates": historical_dates,
                    "prices": [float(p) for p in historical_prices]
                },
                "future_predictions": [
                    {"date": date, "price": round(float(price[0]), 2)} 
                    for date, price in zip(future_dates, future_prices)
                ],
                "model_info": {
                    "last_updated": datetime.fromtimestamp(os.path.getmtime(model_path)).strftime('%Y-%m-%d'),
                    "prediction_days": prediction_days
                }
            }
            
            return jsonify(response)
            
    except Exception as e:
        import traceback
        print(f"LSTM預測錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"預測失敗: {str(e)}"}), 500