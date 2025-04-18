import os
import json
import random
import time
import math 
import numpy as np
import pandas as pd
import yfinance as yf # type: ignore
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
import requests # type: ignore
from talib import SMA, EMA, WMA, KAMA, RSI, STOCH, STOCHRSI, STOCHF, MACD # type: ignore
from flask import jsonify, Response

from . import stock_app_blueprint

# 快取設定
_cache = {
    'tw_categories': {
        'data': None,
        'timestamp': None
    }
}

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

# 快取裝飾器
def cache_categories(duration=24*60*60):  # 預設24小時
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = 'tw_categories'
            now = time.time()
            
            # 檢查快取是否存在且未過期
            if (_cache[cache_key]['data'] is not None and 
                _cache[cache_key]['timestamp'] is not None and 
                now - _cache[cache_key]['timestamp'] < duration):
                print(f"返回快取的台股類別資料, 更新於 {datetime.fromtimestamp(_cache[cache_key]['timestamp'])}")
                return _cache[cache_key]['data']
            
            # 快取不存在或已過期，執行原函數並更新快取
            result = func(*args, **kwargs)
            _cache[cache_key]['data'] = result
            _cache[cache_key]['timestamp'] = now
            return result
        return wrapper
    return decorator

# 自定義 JSON 編碼器處理 NaN 值
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj) if not np.isnan(obj) else None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super(NpEncoder, self).default(obj)

@stock_app_blueprint.route('/api/tw_categories', methods=['GET'])
@retry_on_429(max_retries=5, initial_delay=2)
@cache_categories(duration=24*60*60)  # 24小時快取
def get_tw_stock_categories():
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, 'data', 'twse_listed_stocks.csv')
        json_path = os.path.join(base_dir, 'data', 'tw_stock_categories.json')
        
        # 檢查是否已有處理過的 JSON 檔案
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # 檢查資料是否還有效 (1天內)
                    if data and 'last_updated' in data:
                        last_updated = datetime.strptime(data['last_updated'], '%Y-%m-%d')
                        if (datetime.now() - last_updated).days < 1:
                            return jsonify(data['categories'])
                except:
                    pass  # 如果讀取失敗，重新處理資料
        
        # 讀取 CSV 檔案
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # 確保必要的列名存在
        required_columns = ['有價證券代號', '有價證券名稱', '產業別']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": "CSV 檔案缺少必要的欄位"}), 400
        
        # 重新命名欄位以方便使用
        df = df.rename(columns={
            '有價證券代號': 'symbol',
            '有價證券名稱': 'name',
            '產業別': 'industry'
        })
        
        # 按產業分類股票
        industry_groups = {}
        for industry in df['industry'].unique():
            if pd.isna(industry):
                continue
                
            industry_stocks = []
            for _, row in df[df['industry'] == industry].iterrows():
                symbol = str(row['symbol']).strip()
                name = row['name']
                
                stock_info = {
                    "ticker": symbol,
                    "name": name,
                    "industry": industry
                }
                industry_stocks.append(stock_info)
            
            if industry_stocks:
                industry_groups[industry] = industry_stocks
        
        # 清理 NaN 值
        def clean_nan(obj):
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(i) for i in obj]
            elif isinstance(obj, float) and np.isnan(obj):
                return None
            else:
                return obj
        
        # 整理為需要的輸出格式
        categories = []
        for industry, stocks in industry_groups.items():
            categories.append({
                "industry": industry,
                "stocks": stocks
            })
        
        # 按產業名稱排序
        categories = sorted(categories, key=lambda x: x['industry'])
        
        # 保存結果
        result = {
            "categories": clean_nan(categories),
            "last_updated": datetime.now().strftime('%Y-%m-%d')
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return jsonify(categories)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_app_blueprint.route('/api/tw_stock_data/<symbol>', methods=['GET'])
@retry_on_429(max_retries=5, initial_delay=2)
def get_tw_stock_data(symbol):
    # 台股代號需要加上 .TW 後綴
    tw_symbol = f"{symbol}.TW"
    stock = yf.Ticker(tw_symbol)
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


@stock_app_blueprint.route('/api/tw_ma/<symbol>', methods=['GET'])
def get_tw_stock_machart_data(symbol):
    try:
        # 台股代號加上 .TW 後綴
        tw_symbol = f"{symbol}.TW"
        stock = yf.Ticker(tw_symbol)
        data = stock.history(period="6mo")  # 過去6個月的數據
        
        if data.empty:
            return jsonify({"error": f"無法獲取 {symbol} 的資料"}), 404
        
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


@stock_app_blueprint.route('/api/tw_bias/<symbol>', methods=['GET'])
def get_tw_stock_biaschart_data(symbol):
    try:
        # 台股代號加上 .TW 後綴
        tw_symbol = f"{symbol}.TW"
        stock = yf.Ticker(tw_symbol)
        data = stock.history(period="6mo")  # 過去6個月的數據
        
        if data.empty:
            return jsonify({"error": f"無法獲取 {symbol} 的資料"}), 404
        
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


def update_twse_stock_list():
    """
    從台灣證券交易所更新上市公司資料
    """
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, 'data', 'twse_listed_stocks.csv')
        
        # 使用 pandas 直接從證交所獲取資料
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=open_data"
        stock_list_df = pd.read_csv(url)
        
        # 保存到本地
        stock_list_df.to_csv(csv_path, index=False, encoding='utf-8')
        
        return True
    except Exception as e:
        print(f"更新台股列表失敗: {str(e)}")
        return False


@stock_app_blueprint.route('/api/tw_update_stocks', methods=['GET'])
def update_tw_stocks():
    """API路由用於手動更新台股列表"""
    try:
        success = update_twse_stock_list()
        if success:
            return jsonify({"status": "success", "message": "台股列表更新成功"})
        else:
            return jsonify({"status": "error", "message": "台股列表更新失敗"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

