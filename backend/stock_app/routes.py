import requests # type: ignore
import json
import math
import random
import time
import os
from flask import jsonify # type: ignore
from sklearn.linear_model import LinearRegression # type: ignore
import yfinance as yf # type: ignore
import pandas as pd # type: ignore
from functools import wraps
from talib import SMA, EMA, WMA, KAMA, RSI, STOCH, STOCHRSI, STOCHF, MACD # type: ignore
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import stock_app_blueprint

# 更完整的 headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

_cache = {
    'categories': {
        'data': None,
        'timestamp': None
    }
}

# 建立 session 並更新 headers
session = requests.Session()
session.headers.update(headers)

# 傳入自定義 session 給 yfinance
yf.Ticker.session = session

# 請求重試裝飾器
def retry_on_429(max_retries=5, initial_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if i == max_retries - 1:  # 最後一次重試
                        raise e
                    if "429" in str(e):
                        # 指數退避 + 隨機延遲
                        sleep_time = delay + random.uniform(0, 1)
                        print(f"Rate limit hit, waiting {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                        delay *= 2  # 指數增長延遲時間
                    else:
                        raise e
        return wrapper
    return decorator

def cache_categories(duration=24*60*60):  # 預設24小時
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = _cache['categories']
            now = datetime.now()
            
            # 檢查快取是否有效
            if (cache['data'] is not None and 
                cache['timestamp'] is not None and 
                (now - cache['timestamp']).total_seconds() < duration):
                return cache['data']
            
            # 執行原始函數獲取新數據
            result = func(*args, **kwargs)
            
            # 更新快取
            _cache['categories']['data'] = result
            _cache['categories']['timestamp'] = now
            
            return result
        return wrapper
    return decorator

@stock_app_blueprint.route('/api/stock_data/<symbol>', methods=['GET'])
@retry_on_429(max_retries=10, initial_delay=2) 
def get_stock_chart_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")  # 獲取過去一個月的數據
    info = stock.info
    
    if not info:
        print(f"Invalid symbol: {symbol}")
        return None
    
    previous_close = info.get("previousClose", 0)
    current_price = info.get("currentPrice", 0)
    change = round((current_price - previous_close) / previous_close * 100, 2)
                    

    if data.empty:
        return jsonify({"error": "No data found for symbol"}), 429
    
    # 只取日期和收盤價
    dates = data.index.strftime('%Y-%m-%d').tolist()
    close_prices = data['Close'].tolist()

    return jsonify({"dates": dates, 
                    "close_prices": close_prices, 
                    "change": change, 
                    "current_price": current_price
    })

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
@retry_on_429(max_retries=10, initial_delay=2)  # 增加重試次數和初始延遲
@cache_categories(duration=1*60*60) 
def get_stock_categories():
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, 'data', 'us_stock_list.csv')
        json_path = os.path.join(base_dir, 'data', 'us_stock_categories.json')
        progress_path = os.path.join(base_dir, 'data', 'fetch_progress.json')

        # 檢查進度文件
        if os.path.exists(progress_path):
            try:
                with open(progress_path, 'r') as f:
                    progress_data = json.load(f)
                    if progress_data.get('date') == datetime.now().strftime('%Y-%m-%d') and 'last_processed' not in progress_data:
                        data = progress_data.get('data', [])
                        # 只依照 symbol 排序
                        sorted_data = sorted(data, key=lambda x: x.get('ticker', ''))

                        # 儲存排序後的資料
                        progress_data['data'] = sorted_data
                        with open(progress_path, 'w') as f:
                            json.dump(progress_data, f)
                            
                        return jsonify(sorted_data)
            except json.JSONDecodeError:
                # 如果 JSON 檔案是空的或格式錯誤，創建新的進度檔案
                progress_data = {
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "data": [],
                    "last_processed": None
                }
                with open(progress_path, 'w') as f:
                    json.dump(progress_data, f)

        df = pd.read_csv(csv_path)
        total_stocks = len(df)
        batch_size = 100  # 減少每批次的大小
        num_batches = math.ceil(total_stocks / batch_size)

        stock_data = []
        delay_between_batches = 10  # 增加批次之間的延遲時間
        
        # 繼續處理未完成的進度
        last_processed = None
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                progress_data = json.load(f)
                if progress_data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                    stock_data = progress_data.get('data', [])
                    last_processed = progress_data.get('last_processed')


        def fetch_stock_data(symbol):
            retries = 10
            base_delay = 2
            while retries > 0:
                try:
                    time.sleep(base_delay + random.uniform(0, 1))  # 添加隨機延遲
                    stock = yf.Ticker(symbol)
                    info = stock.info
                    if not info:
                        print(f"Invalid symbol: {symbol}")
                        return None
                    
                    previous_close = info.get("previousClose", 0)
                    current_price = info.get("currentPrice", 0)
                    change = round((current_price - previous_close) / previous_close * 100, 2)
                    
                    return {
                        "ticker": symbol,
                        "name": info.get("shortName", "N/A"),
                        "sector": info.get("sector", "Unknown"),
                        "industry": info.get("industry", "Unknown"),
                        "marketCap": info.get("marketCap", 0),
                        "change": change,
                        "current_price": current_price,
                        "date": datetime.now().strftime('%Y-%m-%d')
                    }
                except Exception as e:
                    if "429" in str(e):
                        print(f"Rate limit hit for {symbol}, retrying in {base_delay} seconds...")
                        time.sleep(base_delay)
                        base_delay *= 2
                        retries -= 1
                    else:
                        print(f"Error fetching data for {symbol}: {e}")
                        break
            return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            for batch_num in range(num_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, total_stocks)
                batch_df = df.iloc[start_idx:end_idx]
                
                # 跳過已處理的股票
                if last_processed:
                    batch_df = batch_df[batch_df['Symbol'] > last_processed]

                futures = {executor.submit(fetch_stock_data, row['Symbol']): row['Symbol'] for index, row in batch_df.iterrows()}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        stock_data.append(result)
                        # 每成功獲取一筆數據就保存進度
                        progress = {
                            "date": datetime.now().strftime('%Y-%m-%d'),
                            "data": stock_data,
                            "last_processed": futures[future]
                        }
                        with open(progress_path, 'w') as f:
                            json.dump(progress, f)

                print(f"Completed batch {batch_num + 1}/{num_batches}")
                time.sleep(delay_between_batches)
        # 所有批次完成後，儲存最終結果（不含 last_processed）
        sorted_data = sorted(stock_data, key=lambda x: x.get('ticker', ''))
        final_progress = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "data": sorted_data
        }
        with open(progress_path, 'w') as f:
            json.dump(final_progress, f)

        # 更新 CSV，移除無效的股票代碼
        # if invalid_symbols:
        #     df = df[~df['Symbol'].isin(invalid_symbols)]
        #     df.to_csv(csv_path, index=False)

        # 保存最終結果
        with open(json_path, 'w') as f:
            json.dump(sorted_data, f)

        return jsonify(sorted_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500