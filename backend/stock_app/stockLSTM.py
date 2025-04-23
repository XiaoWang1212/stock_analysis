import os
import re
from urllib.parse import urljoin
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
from tensorflow.keras.models import Model, load_model, Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.callbacks import EarlyStopping # type: ignore
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup # type: ignore
import requests # type: ignore
import functools
import time
import nltk # type: ignore
import yfinance as yf # type: ignore
import numpy as np
import pandas as pd
from flask import jsonify, request
from datetime import datetime, timedelta
import pickle
import random


from . import stock_app_blueprint

def retry_on_429(max_retries=5, initial_delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        if i < max_retries - 1:
                            print(f"Rate limited. Retrying in {delay} seconds...")
                            time.sleep(delay)
                            delay *= 2  # 指數退避
                        else:
                            raise
                    else:
                        raise
        return wrapper
    return decorator

session = requests.Session()

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
    
sid = SentimentIntensityAnalyzer()

@stock_app_blueprint.route('/api/stock_sentiment/<symbol>', methods=['GET'])
@retry_on_429(max_retries=5, initial_delay=1)
def analysis_stock_sentiment(symbol, days=30):
    try:
        base_url = "https://finance.yahoo.com"
        news_url = f"{base_url}/quote/{symbol}/news"
        
        all_sentiment_scores = []
        titles = []
        article_contents = []
        news_links = []
        news_impacts = []
        news_times = []
        
        try:
            # 高級請求配置
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 108)}.0.{random.randint(4000, 5000)}.{random.randint(0, 150)} Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/search?q=finance"
            }
            
            print(f"嘗試連接 {news_url}...")
            response = session.get(news_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"成功獲取 {news_url} 內容，分析中...")
            
            # 1. 先獲取所有新聞標題和對應的連結
            news_items = []
            news_containers = []
            
            # 嘗試多種選擇器來獲取標題和連結
            selectors = [   
                'li.js-stream-content', 
                'content yf-1y7058a',
                'div.content.yf-1y7058a, li.js-stream-content'
            ]
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    news_containers.extend(elements)
                    print(f"使用選擇器 {selector} 獲取新聞項目")
                
            for container in news_containers:
                title_element = container.find('h3') or container.find('a[data-test="mega-headline"]')
                if not title_element:
                    continue
                    
                title = title_element.get_text().strip()
                
                # 找尋連結
                link_element = container.select_one('a[href]')
                link = link_element.get('href') if link_element else None
                if link and not link.startswith(('http://', 'https://')):
                    link = urljoin(base_url, link)

                # 查找發布時間和來源
                time_text = ""
                time_element = container.select_one('.caas-attr-time-style') or container.select_one('.publishing') or container.select_one('div[class*="Fz(12px)"]')
                
                if time_element:
                    time_text = time_element.get_text().strip()
                
                publish_time = process_time_text(time_text)

                if title and len(title) > 10 and link:
                    news_items.append({
                        'title': title,
                        'link': link,
                        'publish_time': publish_time
                    })
        
            # 如果主選擇器沒有找到足夠的新聞，嘗試備用選擇器
            if len(news_items) < 5:
                for headline in soup.select('h3, h4'):
                    link_parent = headline.find_parent('a', href=True)
                    if link_parent:
                        title = headline.get_text().strip()
                        link = link_parent.get('href')
                        
                        if link and not link.startswith(('http://', 'https://')):
                            link = urljoin(base_url, link)
                            
                        if title and len(title) > 10 and link:
                            news_items.append({'title': title, 'link': link})
            
            print(f"找到 {len(news_items)} 條新聞項目")
            
            # 2. 獲取文章內容（最多20篇文章）
            article_count = min(len(news_items), 20)
            for i, news in enumerate(news_items[:article_count]):
                try:
                    title = news['title']
                    link = news['link'] 
                    publish_time = news.get('publish_time', "")

                    titles.append(title)
                    news_links.append(link)
                    news_times.append(publish_time)
                    
                    print(f"嘗試獲取文章 {i+1}/{article_count}: {title[:30]}...")
                    
                    # 加入隨機延遲，避免被封鎖
                    time.sleep(random.uniform(0.5, 2.0))
                    
                    # 使用不同的請求頭訪問文章
                    article_headers = headers.copy()
                    article_headers["User-Agent"] = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 108)}.0.{random.randint(4000, 5000)}.{random.randint(0, 150)} Safari/537.36"
                    
                    article_response = session.get(link, headers=article_headers, timeout=15)
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # 嘗試找到文章正文內容（不同網站可能有不同的結構）
                    article_text = ""
                    
                    # Yahoo Finance 文章選擇器
                    article_selectors = [
                        'div[data-test-locator="articleBody"]', 
                        'div.caas-body',
                        'div.article-body',
                        'div[class*="content"]',
                        'article',
                        'div[itemprop="articleBody"]'
                    ]
                    
                    for selector in article_selectors:
                        content_div = article_soup.select_one(selector)
                        if content_div:
                            # 提取所有段落
                            paragraphs = content_div.find_all('p')
                            if paragraphs:
                                article_text = ' '.join([p.get_text().strip() for p in paragraphs])
                                if len(article_text) > 100:  # 確保文章內容有最小長度
                                    break
                    
                    if article_text:
                        print(f"成功獲取文章內容，長度: {len(article_text)} 字")
                        article_contents.append(article_text)
                    else:
                        print(f"無法獲取文章內容: {title[:30]}...")
                    
                except Exception as e:
                    print(f"獲取文章時出錯: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"爬取 {news_url} 時出錯: {str(e)}")
        
        # 移除重複標題
        titles = list(set(titles))

        title_link_time_map = {}
        for i, title in enumerate(titles):
            if i < len(news_links) and i < len(news_times):
                title_link_time_map[title] = {
                    "link": news_links[i],
                    "publish_time": news_times[i]
                }
                
        titles = list(title_link_time_map.keys())
        news_links = [title_link_time_map[title]["link"] for title in titles]
        news_times = [title_link_time_map[title]["publish_time"] for title in titles]
        
        print(f"去重後剩餘 {len(titles)} 條新聞標題")
        print(f"成功獲取 {len(article_contents)} 篇文章內容")
        
        # 3. 進行情感分析
        # 金融相關的情感詞彙
        finance_pos_terms = ["rally", "surge", "jump", "gain", "growth", "upgrade", "beat", "bullish", 
                           "outperform", "positive", "upside", "opportunity", "strong", "uptrend"]
        finance_neg_terms = ["fall", "drop", "plunge", "decline", "loss", "downgrade", "miss", "bearish", 
                           "underperform", "negative", "downside", "risk", "weak", "downtrend"]
        
        # 股票相關關鍵詞
        stock_terms = [symbol.lower(), symbol, "stock", "shares", "investor", "market"]
        
        # 分析標題情感
        title_scores = []
        title_impact_links = []
        for i, title in enumerate(titles):
            if i < len(news_links) and title and len(title) > 10:  # 避免過短標題
                # VADER 原始情感分數
                score = sid.polarity_scores(title)
                compound_score = score['compound']
                
                # 發布時間
                pub_time = ""
                if title in title_link_time_map:
                    pub_time = title_link_time_map[title]["publish_time"]
                
                # 金融詞彙增強
                title_lower = title.lower()
                pos_matches = sum(1 for term in finance_pos_terms if term in title_lower)
                neg_matches = sum(1 for term in finance_neg_terms if term in title_lower)
                
                # 根據股票相關性調整權重
                is_stock_specific = any(term in title_lower for term in stock_terms)
                weight = 1.5 if is_stock_specific else 1.0
                
                # 調整情感分數（金融詞彙+股票相關性）
                if -0.1 < compound_score < 0.1:  # 對中性結果進行更多調整
                    if pos_matches > neg_matches:
                        compound_score += 0.1 * pos_matches
                    elif neg_matches > pos_matches:
                        compound_score -= 0.1 * neg_matches
                        
                adjusted_score = compound_score * weight
                adjusted_score = max(-1.0, min(1.0, adjusted_score))  # 限制在-1和1之間

                title_impact_links.append({
                    "title": title,
                    "impact": adjusted_score,
                    "link": news_links[i],
                    "publish_time": pub_time
                })
                
                print(f"標題: {title[:30]}... 原始分數: {compound_score:.4f}, 調整後: {adjusted_score:.4f}")
                title_scores.append(adjusted_score)
                news_impacts.append(adjusted_score)
        
        # 分析文章內容情感
        article_scores = []
        for content in article_contents:
            if content and len(content) > 100:  # 確保有足夠內容進行分析
                # 分段分析長文本，避免VADER處理過長文本的問題
                chunk_size = 1000  # 每個分析塊的大小
                chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                
                chunk_scores = []
                for chunk in chunks:
                    score = sid.polarity_scores(chunk)
                    chunk_scores.append(score['compound'])
                
                # 使用加權平均，給最前面的段落更高的權重
                weighted_scores = []
                for i, score in enumerate(chunk_scores):
                    # 段落權重隨位置遞減
                    weight = 1.0 / (1 + i * 0.3)
                    weighted_scores.append(score * weight)
                
                avg_article_score = sum(weighted_scores) / sum(1.0 / (1 + i * 0.3) for i in range(len(chunk_scores)))
                
                # 檢查文章中的金融詞彙
                pos_matches = sum(1 for term in finance_pos_terms if term in content.lower())
                neg_matches = sum(1 for term in finance_neg_terms if term in content.lower())
                
                # 調整情感分數
                if -0.1 < avg_article_score < 0.1:  # 對中性結果進行調整
                    if pos_matches > neg_matches:
                        avg_article_score += 0.05 * min(5, pos_matches)
                    elif neg_matches > pos_matches:
                        avg_article_score -= 0.05 * min(5, neg_matches)
                
                # 確保分數在-1和1之間
                avg_article_score = max(-1.0, min(1.0, avg_article_score))
                print(f"文章內容情感分數: {avg_article_score:.4f}")
                article_scores.append(avg_article_score)
        
        # 合併標題和文章的情感分數
        # 標題:文章 = 1:2 的權重比例（因為文章包含更多內容細節）
        combined_scores = []
        
        for title_score, article_score in zip(title_scores, article_scores):
            combined_scores.append(title_score * 0.35 + article_score * 0.65)  # 標題權重 35%, 文章權重 65%
        
        # 如果沒有找到新聞或文章，使用備用方案
        if not combined_scores:
            print(f"警告: 沒有為 {symbol} 找到新聞分析結果，使用模擬數據")
            return generate_simulated_sentiment(symbol, days)

        news_times_list = []
        news_titles = []

        for i, title in enumerate(titles):
            if i < len(news_times):
                news_times_list.append(news_times[i])
            news_titles.append(title)
            
        # 計算最終加權平均情感分數
        print(len(combined_scores), len(news_times_list), len(news_titles))
        avg_sentiment = calculate_balanced_sentiment(combined_scores, news_times_list, news_titles)
        
        print(f"{symbol} 最終平均情感分數: {avg_sentiment:.4f}")
        
        top_5_news = sorted(title_impact_links, key=lambda x: abs(x['impact']), reverse=True)[:5]
        
        # 生成情感趨勢，基於真實文章情感
        trend_pattern = generate_sentiment_trend_pattern(avg_sentiment, days)
        
        return {
            "sentiment_trend": trend_pattern,
            "top_news": top_5_news,
            "avg_sentiment": avg_sentiment
        }
        
    except Exception as e:
        print(f"分析 {symbol} 情感時出錯: {str(e)}")
        # 出錯時使用模擬數據
        simulated_data = generate_simulated_sentiment(symbol, days)
        return {
            "sentiment_trend": simulated_data,
            "top_news": [],
            "avg_sentiment": sum(simulated_data) / len(simulated_data) if simulated_data else 0
        }

# 新增：處理時間文本的輔助函數
def process_time_text(time_text):
    """處理從Yahoo Finance獲取的時間文本，轉換為標準格式"""
    if not time_text:
        return ""
        
    try:
        # 解析來源和時間
        source_time_parts = time_text.split('•')
        if len(source_time_parts) > 1:
            source = source_time_parts[0].strip()
            time_part = source_time_parts[1].strip()
        else:
            source = ""
            time_part = time_text.strip()
        
        # 處理時間格式
        if "hours ago" in time_part or "hour ago" in time_part:
            hour_match = re.search(r'(\d+)\s*hour', time_part)
            if hour_match:
                hours = int(hour_match.group(1))
                result = f"{hours}小時前"
                return f"{source} • {result}" if source else result
                
        elif "minutes ago" in time_part or "minute ago" in time_part:
            minute_match = re.search(r'(\d+)\s*minute', time_part)
            if minute_match:
                minutes = int(minute_match.group(1))
                result = f"{minutes}分鐘前"
                return f"{source} • {result}" if source else result
                
        elif "days ago" in time_part or "day ago" in time_part:
            day_match = re.search(r'(\d+)\s*day', time_part)
            if day_match:
                days = int(day_match.group(1))
                result = f"{days}天前"
                return f"{source} • {result}" if source else result
        
        return time_text
    except Exception as e:
        print(f"處理時間文本出錯: {str(e)}")
        return time_text

def calculate_balanced_sentiment(scores, times=None, titles=None):
    """
    計算更均衡的情感平均值，考慮時間衰減和負面新聞放大
    
    參數:
    - scores: 情感分數列表
    - times: 對應的發布時間信息（可選）
    - titles: 對應的標題（可選，用於調試）
    """
    if not scores:
        return 0.0
    
    # 1. 時間權重：根據是否有時間信息計算時間衰減權重
    time_weights = []
    if times:
        # 解析時間信息并計算相對權重
        for time_info in times:
            if "小時前" in str(time_info):
                try:
                    hours = int(re.search(r'(\d+)小時前', str(time_info)).group(1))
                    # 新聞越新權重越大，24小時內權重遞減
                    # 24小時前權重0.5，1小時前權重接近1.0
                    time_weight = 0.5 + 0.5 * (1.0 - min(24.0, float(hours)) / 24.0)
                except:
                    time_weight = 0.7  # 默認時間權重
            elif "分鐘前" in str(time_info):
                time_weight = 1.0  # 非常新的新聞
            else:
                time_weight = 0.7  # 默認時間權重
            time_weights.append(time_weight)
    else:
        # 沒有時間信息，使用平等權重
        time_weights = [1.0] * len(scores)
    
    # 2. 情感權重：負面消息給予更大權重
    sentiment_weights = []
    for score in scores:
        if score < -0.2:  # 明顯負面
            # 負面程度越高，權重越大 (-1的權重為2.5，-0.2的權重為1.1)
            sentiment_weight = 1.0 + min(1.5, abs(score) * 1.5)
        elif score < 0:  # 輕微負面
            sentiment_weight = 1.0 + abs(score) * 0.5
        elif score > 0.5:  # 強烈正面
            sentiment_weight = 0.9  # 降低強烈正面的權重
        elif score > 0:  # 輕微正面
            sentiment_weight = 0.95
        else:  # 中性
            sentiment_weight = 0.8
        sentiment_weights.append(sentiment_weight)
    
    # 3. 計算加權分數
    weighted_scores = []
    total_weight = 0
    
    # 調試信息
    debug_info = []
    
    for i, score in enumerate(scores):
        # 計算這個分數的綜合權重
        combined_weight = time_weights[i] * sentiment_weights[i]
        weighted_score = score * combined_weight
        
        weighted_scores.append(weighted_score)
        total_weight += combined_weight
        
        # 收集調試信息
        if titles and i < len(titles):
            short_title = titles[i][:30] + "..." if len(titles[i]) > 30 else titles[i]
            debug_info.append({
                "title": short_title,
                "score": score,
                "time_weight": time_weights[i],
                "sentiment_weight": sentiment_weights[i],
                "combined_weight": combined_weight,
                "weighted_score": weighted_score
            })
    
    # 計算加權平均
    if total_weight > 0:
        final_score = sum(weighted_scores) / total_weight
    else:
        final_score = 0.0
    
    # 強負面懲罰：如果有多個顯著負面文章(20%文章強烈負面),進一步降低分數
    strong_negative_count = sum(1 for s in scores if s < -0.5)
    if strong_negative_count >= max(2, len(scores) * 0.2):
        negative_penalty = min(0.15, 0.05 * strong_negative_count)
        final_score -= negative_penalty
    
    # 打印調試信息
    print("\n情感分析權重細節:")
    print(f"{'標題':<35} {'原始分數':>10} {'時間權重':>10} {'情感權重':>10} {'綜合權重':>10} {'加權分數':>10}")
    print("-" * 90)
    
    for item in debug_info[:10]:  # 只顯示前10項
        print(f"{item['title']:<35} {item['score']:>10.4f} {item['time_weight']:>10.4f} {item['sentiment_weight']:>10.4f} {item['combined_weight']:>10.4f} {item['weighted_score']:>10.4f}")
    
    if len(debug_info) > 10:
        print(f"...以及其他 {len(debug_info)-10} 項")
    
    print(f"\n強負面文章數量: {strong_negative_count}")
    print(f"總權重: {total_weight:.4f}")
    print(f"最終情感分數: {final_score:.4f}")
    
    # 限制最終分數在 -1 到 1 之間
    return max(-1.0, min(1.0, final_score))

# 生成情感趨勢模式函數
def generate_sentiment_trend_pattern(avg_sentiment, days):
    """生成更自然的情感趨勢模式"""
    # 基於平均情感，創建一個符合市場現實的情感趨勢
    base = avg_sentiment * 0.6  # 基準情感水平
    amplitude = abs(avg_sentiment) * 0.5  # 波動幅度
    
    # 創建一個主要趨勢
    trend = []
    for i in range(days):
        # 使用週期性函數模擬市場情緒的起伏
        cycle1 = np.sin(i / (days/3) * np.pi) * amplitude * 0.7
        cycle2 = np.sin(i / (days/6) * np.pi) * amplitude * 0.3
        
        # 添加一個小的隨機波動
        noise = np.random.normal(0, 0.04)
        
        # 組合基準、主要趨勢和隨機波動
        day_sentiment = base + cycle1 + cycle2 + noise
        
        # 確保值在-1到1之間
        trend.append(max(-1.0, min(1.0, day_sentiment)))
    
    return trend

# 生成模擬情感數據函數
def generate_simulated_sentiment(symbol, days):
    """當無法獲取真實情感數據時，生成模擬數據"""
    np.random.seed(hash(symbol) % 10000)  # 確保相同股票生成相似模式
    
    # 根據股票代碼生成基準情感
    # 轉換股票代碼為數字（簡單哈希）
    symbol_hash = sum(ord(c) for c in symbol) % 100 / 100.0
    base_sentiment = (symbol_hash - 0.5) * 0.4  # -0.2 到 0.2 之間的值
    
    # 生成市場趨勢
    market_trend = np.cumsum(np.random.normal(0, 0.02, days)) * 0.15
    
    sentiment_history = []
    for i in range(days):
        # 基準情感 + 市場趨勢 + 周期性波動 + 隨機噪聲
        periodic = np.sin(i / 14 * 2 * np.pi) * 0.1  # 兩週一個周期
        noise = np.random.normal(0, 0.07)
        day_sentiment = base_sentiment + market_trend[i] + periodic + noise
        sentiment_history.append(max(-1, min(1, day_sentiment)))
    
    print(f"已為 {symbol} 生成模擬情感數據")
    return sentiment_history
    
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(symbol):
    return os.path.join(MODEL_DIR, f"{symbol}_lstm_model.keras")

def get_scaler_path(symbol):
    return os.path.join(MODEL_DIR, f"{symbol}_scaler.pkl")

def get_model_path(symbol, with_sentiment=True):
    """獲取模型路徑，帶有是否包含情感分析的選項"""
    suffix = "_with_sentiment" if with_sentiment else ""
    return os.path.join(MODEL_DIR, f"{symbol}_lstm_model{suffix}.keras")

def get_scaler_path(symbol, with_sentiment=True):
    """獲取縮放器路徑，帶有是否包含情感分析的選項"""
    suffix = "_with_sentiment" if with_sentiment else ""
    return os.path.join(MODEL_DIR, f"{symbol}_scaler{suffix}.pkl")

def create_lstm_model(input_shape, dropout_rate=0.2, include_sentiment=True):
    """
    創建 LSTM 模型，可選擇是否納入情感分析
    input_shape: 輸入數據的形狀
    dropout_rate: Dropout 層的率
    include_sentiment: 是否在模型中加入情感分析
    """
    if include_sentiment:
        # 使用函數式API來處理多輸入
        price_input = Input(shape=(input_shape[0], 1), name='price_input')
        sentiment_input = Input(shape=(1,), name='sentiment_input')
        
        # 價格序列處理
        x = LSTM(units=64, return_sequences=True, recurrent_dropout=0.1)(price_input)
        x = Dropout(dropout_rate)(x)
        x = LSTM(units=64, return_sequences=True)(x)
        x = Dropout(dropout_rate)(x)
        x = LSTM(units=32, return_sequences=False)(x)
        x = Dropout(dropout_rate)(x)
        
        # 合併情感數據
        concat = tf.keras.layers.concatenate([x, sentiment_input])
        
        # 密集層
        x = Dense(units=32, activation='relu')(concat)
        x = Dropout(dropout_rate)(x)
        x = Dense(units=16, activation='relu')(x)
        output = Dense(units=1)(x)
        
        # 建立模型
        model = Model(inputs=[price_input, sentiment_input], outputs=output)
    else:
        # 原始模型（單輸入）
        model = Sequential()
        model.add(LSTM(units=64, return_sequences=True, input_shape=input_shape, 
                       recurrent_dropout=0.1))
        model.add(Dropout(dropout_rate))
        model.add(LSTM(units=64, return_sequences=True))
        model.add(Dropout(dropout_rate))
        model.add(LSTM(units=32, return_sequences=False))
        model.add(Dropout(dropout_rate))
        model.add(Dense(units=32, activation='relu'))
        model.add(Dropout(dropout_rate))
        model.add(Dense(units=16, activation='relu'))
        model.add(Dense(units=1))
    
    # 編譯模型
    model.compile(optimizer=Adam(learning_rate=0.0005), loss='mean_squared_error')
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

# 1. 數據載入與準備函式
def load_stock_data(symbol_full, period="1y"):
    """載入股票數據"""
    stock = yf.Ticker(symbol_full)
    data = stock.history(period=period)
    if data.empty:
        raise ValueError(f"無法獲取股票數據: {symbol_full}")
    return data

def prepare_training_data(data, prediction_days, scaler=None):
    """將原始數據轉換為訓練數據"""
    if scaler is None:
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))
    else:
        scaled_data = scaler.transform(data['Close'].values.reshape(-1, 1))
    
    x_train, y_train = [], []
    for x in range(prediction_days, len(scaled_data)):
        x_train.append(scaled_data[x-prediction_days:x, 0])
        y_train.append(scaled_data[x, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    return x_train, y_train, scaler

# 2. 模型訓練函式
def train_lstm_model(x_train, y_train, sentiment_train=None, include_sentiment=False):
    """訓練LSTM模型"""
    input_shape = (x_train.shape[1], 1)
    model = create_lstm_model(input_shape, include_sentiment=include_sentiment)
    
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    if include_sentiment and sentiment_train is not None:
        model.fit(
            [x_train, sentiment_train], y_train, 
            epochs=25, batch_size=32, verbose=0,
            validation_split=0.2,
            callbacks=[early_stopping]
        )
    else:
        model.fit(x_train, y_train, epochs=25, batch_size=32, verbose=0)
    
    return model

# 3. 預測函式
def predict_future_prices(model, last_sequence, sentiment_data=None, include_sentiment=False, days=7):
    """預測未來價格"""
    future_predictions = []
    
    if include_sentiment and sentiment_data is not None:
        # 確保情感數據足夠
        if len(sentiment_data) >= days:
            future_sentiment = sentiment_data[-days:]
        else:
            # 使用最後一個情感值填充
            last_sentiment = sentiment_data[-1] if sentiment_data else 0
            future_sentiment = [last_sentiment] * days
        
        for i in range(days):
            try:
                # 明確確保維度正確
                current_sequence = last_sequence.copy()  # 複製以避免修改原始數據
                current_sentiment = np.array([future_sentiment[i]]).reshape(1, 1)
                
                # 驗證輸入維度
                print(f"預測第 {i+1} 天: sequence shape={current_sequence.shape}, sentiment shape={current_sentiment.shape}")
                
                # 預測下一天
                next_day = model.predict([current_sequence, current_sentiment], verbose=0)[0]
                future_predictions.append(next_day[0])
                
                # 更新序列
                last_sequence = np.roll(current_sequence, -1, axis=1)
                last_sequence[0, -1, 0] = next_day[0]
                
            except Exception as e:
                print(f"預測第 {i+1} 天出錯: {e}")
                # 如果預測失敗，使用上一天的預測值（或初始值）
                last_value = future_predictions[-1] if future_predictions else last_sequence[0, -1, 0]
                future_predictions.append(last_value)
    else:
        # 不使用情感數據的預測（現有代碼）
        for _ in range(days):
            next_day = model.predict(last_sequence, verbose=0)[0]
            future_predictions.append(next_day[0])
            
            # 更新序列
            new_sequence = np.copy(last_sequence)
            new_sequence = new_sequence[:, 1:, :]
            new_sequence = np.append(new_sequence, [[[next_day[0]]]], axis=1)
            last_sequence = new_sequence
    
    return np.array(future_predictions).reshape(-1, 1)

# 4. 計算指標函式
def calculate_metrics(actual_prices, predicted_prices):
    """計算預測指標"""
    if len(actual_prices) > 0 and len(predicted_prices) > 0:
        mse = np.mean((actual_prices - predicted_prices.flatten())**2)
        rmse = np.sqrt(mse)
        accuracy = max(0, 100 - min(100, (rmse / np.mean(actual_prices)) * 100))
    else:
        accuracy = 0
        rmse = 0
    
    return accuracy, rmse

def get_sentiment_data(symbol_full, include_sentiment):
    """獲取股票情感數據"""
    if not include_sentiment:
        return None, None, None
    
    try:
        # 使用我們已定義的情感分析函數
        sentiment_result = analysis_stock_sentiment(symbol_full, days=365)  # 獲取足夠的情感數據

        if isinstance(sentiment_result, dict):
            sentiment_trend = sentiment_result.get("sentiment_trend", [])
            top_news = sentiment_result.get("top_news", [])
            avg_sentiment = sentiment_result.get("avg_sentiment", 0)
        else:
            # 如果返回的不是字典，則使用預設值
            sentiment_trend = sentiment_result
            top_news = []
            avg_sentiment = sum(sentiment_result) / len(sentiment_result) if sentiment_result else 0
        return sentiment_trend, top_news, avg_sentiment
    except Exception as e:
        print(f"無法獲取情感數據: {e}, 將不使用情感分析")
        return None, None, None

# 5. 主API函式 - 大幅精簡
@stock_app_blueprint.route('/api/lstm_predict/<symbol>/<market>', methods=['GET'])
def lstm_predict_stock(symbol, market='US'):
    try:
        # 參數處理
        if market == 'TW':
            symbol_full = f"{symbol}.TW"
        else:
            symbol_full = symbol
            
        model_path = get_model_path(symbol_full)
        scaler_path = get_scaler_path(symbol_full)
        prediction_days = 60
        
        force_retrain = request.args.get('retrain', 'false').lower() == 'true'
        include_sentiment = request.args.get('sentiment', 'true').lower() == 'true'
        
        # 獲取情感數據
        sentiment_data, top_5_news, avg_sentiment = get_sentiment_data(symbol_full, include_sentiment)
        
        # 根據是否需要重新訓練模型，調用不同的處理邏輯
        if os.path.exists(model_path) and os.path.exists(scaler_path) and not force_retrain:
            response = handle_existing_model(symbol_full, market, model_path, scaler_path, 
                                            prediction_days, sentiment_data, include_sentiment, top_5_news)
        else:
            response = handle_model_training(symbol_full, market, model_path, scaler_path, 
                                           prediction_days, sentiment_data, include_sentiment, top_5_news)
        
        return jsonify(response)
            
    except Exception as e:
        import traceback
        print(f"LSTM預測錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"預測失敗: {str(e)}"}), 500

# 6. 處理現有模型的函式
def handle_existing_model(symbol_full, market, model_path, scaler_path, 
                         prediction_days, sentiment_data, include_sentiment, top_5_news):
    """使用現有模型預測"""
    # 載入模型和縮放器
    model = load_model(model_path)
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # 獲取近期數據
    period = "6mo" if market == 'TW' else "3mo"
    recent_data = load_stock_data(symbol_full, period)
    
    if recent_data.empty:
        raise ValueError(f"無法獲取近期數據: {symbol_full}")
    
    # 準備數據
    prices = recent_data['Close'].values.reshape(-1, 1)
    scaled_prices = scaler.transform(prices)
    
    # 確保有足夠的數據
    if len(scaled_prices) < prediction_days:
        raise ValueError(f"數據不足以進行預測 (需要至少 {prediction_days} 個數據點)")
    
    # 準備測試數據
    x_test = []
    for i in range(prediction_days, len(scaled_prices)):
        x_test.append(scaled_prices[i-prediction_days:i, 0])
    
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    # 檢查是否為帶有情感輸入的模型
    is_sentiment_model = isinstance(model.input, list) if hasattr(model, 'input') else False
    
    # 進行預測
    if is_sentiment_model and sentiment_data is not None:
        # 使用最近的情感數據
        if len(x_test) > 0:
            if len(sentiment_data) >= len(x_test):
                recent_sentiment = sentiment_data[-len(x_test):]
            else:
                # 如果情感數據不足，使用最近的情感值填充
                last_sentiment = sentiment_data[-1] if sentiment_data else 0
                recent_sentiment = [last_sentiment] * len(x_test)
            
            # 將情感數據轉換為模型需要的形狀
            sentiment_input = np.array(recent_sentiment).reshape(-1, 1)
            
            # 確保輸入數據的維度匹配
            if sentiment_input.shape[0] != x_test.shape[0]:
                print(f"警告: 情感數據長度 ({sentiment_input.shape[0]}) 與測試數據長度 ({x_test.shape[0]}) 不匹配")
                # 截取或填充情感數據以匹配 x_test 長度
                if sentiment_input.shape[0] > x_test.shape[0]:
                    sentiment_input = sentiment_input[-x_test.shape[0]:]
                else:
                    padding = np.full((x_test.shape[0] - sentiment_input.shape[0], 1), sentiment_input[-1][0])
                    sentiment_input = np.vstack((sentiment_input, padding))
            
            try:
                predicted_prices = model.predict([x_test, sentiment_input], verbose=0)
            except Exception as e:
                print(f"使用情感模型預測失敗: {e}, 嘗試不使用情感")
                # 如果帶情感預測失敗，則嘗試只用價格數據預測
                predicted_prices = model.predict(x_test, verbose=0)
        else:
            predicted_prices = np.array([])
    else:
        predicted_prices = model.predict(x_test, verbose=0) if len(x_test) > 0 else np.array([])
    
    predicted_prices = scaler.inverse_transform(predicted_prices) if len(predicted_prices) > 0 else np.array([])
    
    # 計算預測準確性
    if len(x_test) > 0 and len(predicted_prices) > 0:
        actual_prices = recent_data['Close'].iloc[-len(predicted_prices):].values
        accuracy, rmse = calculate_metrics(actual_prices, predicted_prices)
    else:
        accuracy, rmse = 0, 0
    
    # 預測未來價格
    last_sequence = scaled_prices[-prediction_days:].reshape(1, prediction_days, 1)
    future_prices = predict_future_prices(
        model, last_sequence, sentiment_data, 
        include_sentiment and is_sentiment_model and sentiment_data is not None
    )
    
    # 反歸一化獲取實際價格
    future_prices = scaler.inverse_transform(future_prices)
    
    # 計算未來日期
    last_date = recent_data.index[-1]
    future_dates = generate_future_dates(last_date)
    
    # 獲取當前情感值
    current_sentiment = sentiment_data[-1] if sentiment_data is not None else 0
    
    # 計算價格變化百分比
    current_price = float(recent_data['Close'].iloc[-1])
    next_price = float(future_prices[0][0]) if len(future_prices) > 0 else current_price
    price_change = ((next_price - current_price) / current_price) * 100
    
    # 計算歷史資料
    historical_dates = recent_data.index[-30:].strftime('%Y-%m-%d').tolist()
    historical_prices = recent_data['Close'].iloc[-30:].tolist()
    
    # 創建模型信息
    model_info = {
        "last_updated": datetime.fromtimestamp(os.path.getmtime(model_path)).strftime('%Y-%m-%d'),
        "prediction_days": prediction_days,
        "includes_sentiment": is_sentiment_model and sentiment_data is not None
    }
    
    # 創建情感數據
    sentiment_viz_data = None
    if sentiment_data is not None:
        sentiment_viz_data = {
            "recent": [float(s) for s in sentiment_data[-30:]] if len(sentiment_data) >= 30 else [float(s) for s in sentiment_data],
            "future": [float(s) for s in sentiment_data[-7:]] if len(sentiment_data) >= 7 else [float(s) for s in sentiment_data[:7]]
        }
    
    return format_response(
        symbol_full, current_price, next_price, price_change,
        accuracy, current_sentiment, rmse,
        historical_dates, historical_prices,
        future_dates, future_prices,
        model_info, sentiment_viz_data, top_5_news
    )

# 7. 處理模型訓練的函式
def handle_model_training(symbol_full, market, model_path, scaler_path, 
                         prediction_days, sentiment_data, include_sentiment, top_5_news):
    """訓練新模型並預測"""
    # 載入和準備數據
    data = load_stock_data(symbol_full, "1y")
    x_train, y_train, scaler = prepare_training_data(data, prediction_days)
    
    # 準備情感數據
    sentiment_train = None
    if include_sentiment and sentiment_data is not None:
        # 取最近的情感數據與訓練數據對齊
        if len(sentiment_data) >= len(y_train):
                    # 有足夠的情感數據
            sentiment_train = np.array(sentiment_data[-len(y_train):]).reshape(-1, 1)
        else:
            # 情感數據不足，使用已有數據循環填充
            repeat_times = (len(y_train) // len(sentiment_data)) + 1
            extended_sentiment = sentiment_data * repeat_times
            sentiment_train = np.array(extended_sentiment[:len(y_train)]).reshape(-1, 1)    
        
        print(f"訓練數據維度: x_train={x_train.shape}, y_train={y_train.shape}, sentiment_train={sentiment_train.shape}")

    # 訓練模型
    model = train_lstm_model(x_train, y_train, sentiment_train, include_sentiment)
    
    # 保存模型和縮放器
    model.save(model_path)
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    # 準備測試數據
    recent_data = data.iloc[-100:]  # 用最近100天數據進行評估
    prices = recent_data['Close'].values.reshape(-1, 1)
    scaled_prices = scaler.transform(prices)
    
    x_test = []
    for i in range(prediction_days, len(scaled_prices)):
        x_test.append(scaled_prices[i-prediction_days:i, 0])
    
    x_test = np.array(x_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    # 進行預測
    if include_sentiment and sentiment_data is not None:
        # 確保數據維度匹配
        if len(sentiment_data) >= len(x_test):
            recent_sentiment = sentiment_data[-len(x_test):]
        else:
            # 情感數據不足，使用最後一個值填充
            last_sentiment = sentiment_data[-1] if sentiment_data else 0
            recent_sentiment = [last_sentiment] * len(x_test)
            
        sentiment_input = np.array(recent_sentiment).reshape(-1, 1)
        
        # 確保輸入維度匹配
        if sentiment_input.shape[0] != x_test.shape[0]:
            if sentiment_input.shape[0] > x_test.shape[0]:
                sentiment_input = sentiment_input[-x_test.shape[0]:]
            else:
                padding = np.full((x_test.shape[0] - sentiment_input.shape[0], 1), sentiment_input[-1][0])
                sentiment_input = np.vstack((sentiment_input, padding))
        
        try:
            predicted_prices = model.predict([x_test, sentiment_input], verbose=0)
        except Exception as e:
            print(f"訓練模型預測失敗: {e}")
            predicted_prices = np.zeros((len(x_test), 1))
    else:
        predicted_prices = model.predict(x_test, verbose=0)
    
    predicted_prices = scaler.inverse_transform(predicted_prices)
    
    # 計算預測準確性
    actual_prices = recent_data['Close'].iloc[-len(predicted_prices):].values
    accuracy, rmse = calculate_metrics(actual_prices, predicted_prices)
    
    # 預測未來價格
    last_sequence = scaled_prices[-prediction_days:].reshape(1, prediction_days, 1)
    future_prices = predict_future_prices(model, last_sequence, sentiment_data, include_sentiment)
    future_prices = scaler.inverse_transform(future_prices)
    
    # 計算未來日期
    last_date = recent_data.index[-1]
    future_dates = generate_future_dates(last_date)
    
    # 獲取當前情感值
    current_sentiment = sentiment_data[-1] if sentiment_data is not None else 0
    
    # 計算價格變化百分比
    current_price = float(recent_data['Close'].iloc[-1])
    next_price = float(future_prices[0][0]) if len(future_prices) > 0 else current_price
    price_change = ((next_price - current_price) / current_price) * 100
    
    # 計算歷史資料
    historical_dates = recent_data.index[-30:].strftime('%Y-%m-%d').tolist()
    historical_prices = recent_data['Close'].iloc[-30:].tolist()
    
    # 創建模型信息
    model_info = {
        "last_updated": datetime.now().strftime('%Y-%m-%d'),
        "prediction_days": prediction_days,
        "includes_sentiment": include_sentiment and sentiment_data is not None
    }
    
    # 創建情感數據
    sentiment_viz_data = None
    if sentiment_data is not None:
        sentiment_viz_data = {
            "recent": [float(s) for s in sentiment_data[-30:]] if len(sentiment_data) >= 30 else [float(s) for s in sentiment_data],
            "future": [float(s) for s in sentiment_data[-7:]] if len(sentiment_data) >= 7 else [float(s) for s in sentiment_data[:7]]
        }
    
    return format_response(
        symbol_full, current_price, next_price, price_change,
        accuracy, current_sentiment, rmse,
        historical_dates, historical_prices,
        future_dates, future_prices,
        model_info, sentiment_viz_data, top_5_news
    )

# 8. 格式化響應的函式
def format_response(symbol, current_price, next_price, price_change, accuracy, 
                   sentiment_score, rmse, historical_dates, historical_prices, 
                   future_dates, future_prices, model_info, sentiment_data=None, top_5_news=None):
    """格式化API響應"""
    response = {
        "symbol": symbol,
        "current_price": current_price,
        "predicted_next_price": next_price,
        "price_change_percent": float(price_change),
        "prediction_accuracy": float(accuracy),
        "sentiment_score": float(sentiment_score),
        "sentiment_impact": "高" if abs(sentiment_score) > 0.2 else "中" if abs(sentiment_score) > 0.05 else "低",
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
        "model_info": model_info
    }
    
    if sentiment_data is not None:
        response["sentiment_data"] = sentiment_data

    if top_5_news:
        response["top_5_news"] = [
            {
                "title": item["title"],
                "impact": float(item["impact"]),
                "impact_direction": "正面" if item["impact"] > 0 else "負面" if item["impact"] < 0 else "中性",
                "link": item["link"],
                "publish_time": item["publish_time"],
            }
            for item in top_5_news
        ]
    
    return response