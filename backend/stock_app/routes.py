from flask import jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense
from datetime import datetime, timedelta
from . import stock_app_blueprint
 
@stock_app_blueprint.route('/api/data', methods=['GET'])
def get_stocks():
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NFLX", "NVDA", "BABA", "INTC"]
    stocks = []

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            stocks.append({"symbol": symbol, "price": round(price, 2)})
        else:
            stocks.append({"symbol": symbol, "price": None})

    return jsonify({"stocks": stocks})

@stock_app_blueprint.route('/api/stock_data/<symbol>', methods=['GET'])
def get_stock_chart_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")  # 獲取過去一個月的數據

    if data.empty:
        return jsonify({"error": "No data found for symbol"}), 404
    
    # 只取日期和收盤價
    dates = data.index.strftime('%Y-%m-%d').tolist()
    close_prices = data['Close'].tolist()
    
    return jsonify({"dates": dates, "close_prices": close_prices})

@stock_app_blueprint.route('/api/predict/<symbol>', methods=['GET'])
def predict_stock(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1y")  # 獲取過去一年的數據

    if data.empty:
        return jsonify({"error": "No data found for symbol"}), 404
    
     # 準備數據
    data['Date'] = data.index
    data['Date'] = pd.to_datetime(data['Date'])
    data['Date'] = data['Date'].map(datetime.toordinal)
    
    X = data[['Date']]
    y = data['Close']
    
    # 訓練模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 預測未來價格
    future_date = datetime.now() + timedelta(days=1)
    future_date_ordinal = datetime.toordinal(future_date)
    predicted_price = model.predict([[future_date_ordinal]])[0]
    
    return jsonify({"symbol": symbol, "predicted_price": round(predicted_price, 2)})

# @stock_app_blueprint.route('/api/predict/<symbol>', methods=['GET'])
# def predict_stock(symbol):
#     stock = yf.Ticker(symbol)
#     data = stock.history(period="1y")  # 獲取過去一年的數據

#     if data.empty:
#         return jsonify({"error": "No data found for symbol"}), 404
    
#     # 準備數據
#     data['Close'] = data['Close'].astype(float)
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

#     # 創建訓練數據集
#     prediction_days = 60
#     x_train, y_train = [], []

#     for x in range(prediction_days, len(scaled_data)):
#         x_train.append(scaled_data[x-prediction_days:x, 0])
#         y_train.append(scaled_data[x, 0])

#     x_train, y_train = np.array(x_train), np.array(y_train)
#     x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

#     # 建立 LSTM 模型
#     model = Sequential()
#     model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
#     model.add(LSTM(units=50))
#     model.add(Dense(units=1))

#     model.compile(optimizer='adam', loss='mean_squared_error')
#     model.fit(x_train, y_train, epochs=25, batch_size=32)

#     # 準備測試數據
#     test_data = stock.history(period="1mo")
#     total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)
#     model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
#     model_inputs = model_inputs.reshape(-1, 1)
#     model_inputs = scaler.transform(model_inputs)

#     x_test = []
#     for x in range(prediction_days, len(model_inputs)):
#         x_test.append(model_inputs[x-prediction_days:x, 0])

#     x_test = np.array(x_test)
#     x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

#     # 預測未來價格
#     predicted_price = model.predict(x_test)
#     predicted_price = scaler.inverse_transform(predicted_price)

#     return jsonify({"symbol": symbol, "predicted_price": round(predicted_price[-1][0], 2)})