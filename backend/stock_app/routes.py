import json
from flask import jsonify
import yfinance as yf
import pandas as pd
from talib import SMA, EMA, WMA, KAMA, RSI, STOCH, STOCHRSI, STOCHF, MACD
from sklearn.linear_model import LinearRegression
import os
import time

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

@stock_app_blueprint.route('/api/ma/<symbol>', methods=['GET'])
def get_stock_machart_data(symbol):
    try:
        # 獲取股票數據
        stock = yf.Ticker(symbol)
        data = stock.history(period="6mo")  # 過去6個月的數據
        if data.empty:
            return jsonify({"error": "No data available for the symbol"}), 404

        # 數據處理
        data['SMA_5'] = SMA(data['Close'], timeperiod=5)
        data['SMA_20'] = SMA(data['Close'], timeperiod=20)
        data['SMA_60'] = SMA(data['Close'], timeperiod=60)
        data['EMA_5'] = EMA(data['Close'], timeperiod=5)
        data['EMA_20'] = EMA(data['Close'], timeperiod=20)
        data['WMA_5'] = WMA(data['Close'], timeperiod=5)
        data['WMA_20'] = WMA(data['Close'], timeperiod=20)
        data['KAMA_5'] = KAMA(data['Close'], timeperiod=10)
        data['KAMA_20'] = KAMA(data['Close'], timeperiod=10)
        data['RSI_6'] = RSI(data['Close'], timeperiod=6)
        data['RSI_24'] = RSI(data['Close'], timeperiod=24)
        macd, macd_signal, macd_hist = MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        data['MACD'] = macd # DIF
        data['MACD_Signal'] = macd_signal # MACD
        slowk, slowd = STOCH(data['High'], data['Low'], data['Close'], fastk_period=9, slowk_period=3, slowd_period=3)
        data['SlowK'] = slowk
        data['SlowD'] = slowd
        fastk, fastd = STOCHRSI(data['Close'], timeperiod=6, fastk_period=9)
        data['STOCHRSI_FastK'] = fastk
        data['STOCHRSI_FastD'] = fastd
        fastk, fastd = STOCHF(data['High'], data['Low'], data['Close'], fastk_period=9, fastd_period=3)
        data['STOCHF_FastK'] = fastk
        data['STOCHF_FastD'] = fastd

        # 將 NaN 值轉換為 None
        data = data.where(pd.notnull(data), None)
        
        # 數據格式化
        data = data.reset_index()
        result = { 
            "dates": data['Date'].dt.strftime('%Y-%m-%d').tolist(),
            "open_prices": data['Open'].tolist(),
            "high_prices": data['High'].tolist(),
            "low_prices": data['Low'].tolist(),
            "close_prices": data['Close'].tolist(),
            "sma_5": [None if pd.isna(x) else x for x in data['SMA_5'].tolist()],
            "sma_20": [None if pd.isna(x) else x for x in data['SMA_20'].tolist()],
            "sma_60": [None if pd.isna(x) else x for x in data['SMA_60'].tolist()],
            "ema_5": [None if pd.isna(x) else x for x in data['EMA_5'].tolist()],
            "ema_20": [None if pd.isna(x) else x for x in data['EMA_20'].tolist()],
            "wma_5": [None if pd.isna(x) else x for x in data['WMA_5'].tolist()],
            "wma_20": [None if pd.isna(x) else x for x in data['WMA_20'].tolist()],
            "kama_5": [None if pd.isna(x) else x for x in data['KAMA_5'].tolist()],
            "kama_20": [None if pd.isna(x) else x for x in data['KAMA_20'].tolist()],
            "rsi_6": [None if pd.isna(x) else x for x in data['RSI_6'].tolist()],
            "rsi_24": [None if pd.isna(x) else x for x in data['RSI_24'].tolist()],
            "macd": [None if pd.isna(x) else x for x in data['MACD'].tolist()],
            "macd_signal": [None if pd.isna(x) else x for x in data['MACD_Signal'].tolist()],
            "slowk": [None if pd.isna(x) else x for x in data['SlowK'].tolist()],
            "slowd": [None if pd.isna(x) else x for x in data['SlowD'].tolist()],
            "stochrsi_fastk": [None if pd.isna(x) else x for x in data['STOCHRSI_FastK'].tolist()],
            "stochrsi_fastd": [None if pd.isna(x) else x for x in data['STOCHRSI_FastD'].tolist()],
            "stochf_fastk": [None if pd.isna(x) else x for x in data['STOCHF_FastK'].tolist()],
            "stochf_fastd": [None if pd.isna(x) else x for x in data['STOCHF_FastD'].tolist()],
            "volumes": data['Volume'].tolist(),
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stock_app_blueprint.route('/api/bias/<symbol>', methods=['GET'])
def get_stock_biaschart_data(symbol):
    try:
        # 獲取股票數據
        stock = yf.Ticker(symbol)
        data = stock.history(period="6mo")  # 過去6個月的數據
        if data.empty:
            return jsonify({"error": "No data available for the symbol"}), 404

        # 數據處理
        data['SMA_5'] = SMA(data['Close'], timeperiod=5)
        data['SMA_10'] = SMA(data['Close'], timeperiod=10)
        data['SMA_20'] = SMA(data['Close'], timeperiod=20)
        data['SMA_60'] = SMA(data['Close'], timeperiod=60)
        data[['SMA_10', 'SMA_20']] = data[['SMA_10', 'SMA_20']].ffill()

        # 計算BIAS
        data['BIAS_10'] = (data['Close'] - SMA(data['Close'], timeperiod=10)) / SMA(data['Close'], timeperiod=10) * 100
        data['BIAS_20'] = (data['Close'] - SMA(data['Close'], timeperiod=20)) / SMA(data['Close'], timeperiod=20) * 100
        
        data['BIAS_DIFF'] = data['BIAS_10'] - data['BIAS_20']

        # 將 NaN 值轉換為 None
        data = data.where(pd.notnull(data), None)
        
        # 數據格式化
        data = data.reset_index()
        result = {
            "dates": data['Date'].dt.strftime('%Y-%m-%d').tolist(),
            "close_prices": data['Close'].tolist(),
            "open_prices": data['Open'].tolist(),
            "high_prices": data['High'].tolist(),
            "low_prices": data['Low'].tolist(),
            "sma_5": [None if pd.isna(x) else x for x in data['SMA_5'].tolist()],
            "sma_20": [None if pd.isna(x) else x for x in data['SMA_20'].tolist()],
            "sma_60": [None if pd.isna(x) else x for x in data['SMA_60'].tolist()],
            "bias_10": [None if pd.isna(x) else x for x in data['BIAS_10'].tolist()],
            "bias_20": [None if pd.isna(x) else x for x in data['BIAS_20'].tolist()],
            "bias_diff": [None if pd.isna(x) else x for x in data['BIAS_DIFF'].tolist()],
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@stock_app_blueprint.route('/api/categories', methods=['GET'])
def get_stock_categories():
    try:
        # 獲取當前檔案的絕對路徑
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, 'data', 'us_stock_list.csv')
        json_path = os.path.join(base_dir, 'data', 'us_stock_categories.json')
        
        # 如果 JSON 檔案存在，檢查數據日期
        if os.path.exists(json_path):
            with open(json_path, 'r') as json_file:
                try:
                    stock_data = json.load(json_file)
                    # 檢查數據日期是否是當天
                    if stock_data and 'date' in stock_data[0]:
                        last_update = datetime.strptime(stock_data[0]['date'], '%Y-%m-%d').date()
                        if last_update == datetime.now().date():
                            return jsonify(stock_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {json_path}")

        
        # 讀取 CSV 檔案
        df = pd.read_csv(csv_path)

        stock_data = []
        invalid_symbols = []

        for index, row in df.iterrows():
            symbol = row['Symbol']  # 假設你的 CSV 有 Symbol 欄位
            retries = 10
            while retries > 0:
                try:
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period="1d")
                    info = stock.info
                    current_price = info.get("currentPrice", 0)
                    previous_close = info.get("regularMarketPreviousClose", 0)
                    sector = info.get("sector", "Unknown")
                    industry = info.get("industry", "Unknown")
                    if sector == "Unknown" or industry == "Unknown":
                        print(f"Invalid sector or industry for {symbol}")
                        invalid_symbols.append(symbol)
                        break
                    if current_price == 0 and previous_close == 0:
                        print(f"No price data for {symbol}")
                        invalid_symbols.append(symbol)
                        break
                    change_percent = info.get("regularMarketChangePercent", 0)
                    if change_percent == 0 and previous_close != 0:
                        change_percent = round(((current_price - previous_close) / previous_close) * 100, 2)
                    stock_data.append({
                        "ticker": symbol,
                        "name": info.get("shortName", "N/A"),
                        "sector": sector,
                        "industry": industry,
                        "marketCap": info.get("marketCap", 0),
                        "change": change_percent,
                        "date": datetime.now().strftime('%Y-%m-%d')
                    })
                    break
                except Exception as e:
                    if "429" in str(e):
                        print(f"Too many requests for {symbol}, retrying...")
                        time.sleep(5)  # 延遲 5 秒後重試
                        retries -= 1
                    else:
                        print(f"Error fetching data for {symbol}: {e}")
                        invalid_symbols.append(symbol)
                        break
            
         # 刪除無效的股票代碼
        if invalid_symbols:
            df = df[~df['Symbol'].isin(invalid_symbols)]
            df.to_csv(csv_path, index=False)
            print(f"Removed invalid symbols: {invalid_symbols}")
            
        with open(json_path, 'w') as json_file:
            json.dump(stock_data, json_file)
            print(f"Saved data to {json_path}")
            
        return jsonify(stock_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500