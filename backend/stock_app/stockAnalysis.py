# import numpy as np
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import LSTM, Dense, Dropout
# from tensorflow.keras.optimizers import Adam
# from sklearn.preprocessing import MinMaxScaler
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# import requests
# from bs4 import BeautifulSoup
# import re
# import nltk

# # 下載必要的NLTK資源(首次運行時需要)
# try:
#     nltk.data.find('vader_lexicon')
# except LookupError:
#     nltk.download('vader_lexicon')

# # 情感分析工具初始化
# sid = SentimentIntensityAnalyzer()

# # LSTM模型建構函數
# def create_lstm_model(input_shape, dropout_rate=0.2):
#     model = Sequential()
#     model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
#     model.add(Dropout(dropout_rate))
#     model.add(LSTM(units=50, return_sequences=False))
#     model.add(Dropout(dropout_rate))
#     model.add(Dense(units=25))
#     model.add(Dense(units=1))
#     model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
#     return model

# # 獲取新聞情感數據
# @retry_on_429(max_retries=5, initial_delay=2)
# def get_stock_sentiment(symbol, days=30):
#     try:
#         # 基本URL（這裡使用Yahoo Finance，您可能需要更換為其他新聞源）
#         base_url = f"https://finance.yahoo.com/quote/{symbol}/news"
        
#         response = session.get(base_url)
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # 找到新聞標題
#         news_titles = []
#         news_elements = soup.find_all('h3', class_='Mb(5px)')
        
#         for element in news_elements[:min(20, len(news_elements))]:  # 最多取前20條新聞
#             news_titles.append(element.get_text())
        
#         # 對每個標題進行情感分析
#         sentiment_scores = []
#         for title in news_titles:
#             score = sid.polarity_scores(title)
#             sentiment_scores.append(score['compound'])  # 使用複合情感分數
        
#         # 如果沒有找到新聞，返回中性情感
#         if not sentiment_scores:
#             return [0.0] * days
            
#         # 計算平均情感分數
#         avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
#         # 填充歷史天數
#         # 實際實現中，您應該存儲每天的情感數據，這裡簡化處理
#         sentiment_history = [avg_sentiment] * days
        
#         return sentiment_history
#     except Exception as e:
#         print(f"Error fetching sentiment for {symbol}: {e}")
#         return [0.0] * days  # 出錯時返回中性情感

# @stock_app_blueprint.route('/api/predict_lstm/<symbol>', methods=['GET'])
# def predict_stock_lstm(symbol):
#     try:
#         # 1. 獲取股票數據
#         stock = yf.Ticker(symbol)
#         data = stock.history(period="6mo")  # 獲取過去6個月數據
        
#         if data.empty:
#             return jsonify({"error": "No data available for the symbol"}), 404
        
#         # 2. 添加技術指標
#         data['SMA_5'] = SMA(data['Close'], timeperiod=5)
#         data['SMA_20'] = SMA(data['Close'], timeperiod=20)
#         data['RSI_14'] = RSI(data['Close'], timeperiod=14)
        
#         # 刪除含有NaN的行
#         data = data.dropna()
        
#         # 3. 獲取情感分析數據
#         sentiment_history = get_stock_sentiment(symbol, len(data))
#         data['Sentiment'] = sentiment_history[-len(data):]
        
#         # 4. 數據準備
#         feature_columns = ['Close', 'Volume', 'SMA_5', 'SMA_20', 'RSI_14', 'Sentiment']
#         target_column = 'Close'
        
#         # 歸一化數據
#         scaler_features = MinMaxScaler(feature_range=(0, 1))
#         scaler_target = MinMaxScaler(feature_range=(0, 1))
        
#         scaled_features = scaler_features.fit_transform(data[feature_columns])
#         scaled_target = scaler_target.fit_transform(data[[target_column]])
        
#         # 創建時間序列數據
#         X, y = [], []
#         time_steps = 60  # 使用前60天的數據預測下一天
        
#         for i in range(time_steps, len(scaled_features)):
#             X.append(scaled_features[i-time_steps:i])
#             y.append(scaled_target[i])
        
#         X, y = np.array(X), np.array(y)
        
#         # 分割訓練和測試數據
#         train_split = int(0.8 * len(X))
#         X_train, X_test = X[:train_split], X[train_split:]
#         y_train, y_test = y[:train_split], y[train_split:]
        
#         # 5. 建立並訓練模型
#         input_shape = (X_train.shape[1], X_train.shape[2])
#         model = create_lstm_model(input_shape)
#         model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)
        
#         # 6. 評估模型
#         y_pred = model.predict(X_test)
        
#         # 反歸一化
#         y_test_actual = scaler_target.inverse_transform(y_test)
#         y_pred_actual = scaler_target.inverse_transform(y_pred)
        
#         # 計算評估指標
#         mse = np.mean((y_test_actual - y_pred_actual)**2)
#         rmse = np.sqrt(mse)
        
#         # 7. 預測未來價格
#         latest_data = scaled_features[-time_steps:]
#         latest_data = np.reshape(latest_data, (1, time_steps, len(feature_columns)))
#         future_pred = model.predict(latest_data)
#         future_price = scaler_target.inverse_transform(future_pred)[0][0]
        
#         # 計算預測準確度（以RMSE為基礎）
#         # 這是一個簡化的計算方式，您可以使用更複雜的方法來評估準確度
#         last_price = data['Close'].iloc[-1]
#         accuracy = max(0, 100 - min(100, (rmse / last_price) * 100))
        
#         # 計算5天和30天的預測趨勢
#         trend_5day = []
#         trend_30day = []
        
#         # 模擬未來5天
#         future_features = latest_data.copy()
#         for _ in range(5):
#             pred = model.predict(future_features)
#             trend_5day.append(float(scaler_target.inverse_transform(pred)[0][0]))
            
#             # 更新特徵用於下一天預測（簡化處理）
#             # 實際應用中，您需要更新所有特徵，包括技術指標和情感數據
#             new_row = future_features[0, -1:].copy()
#             new_row[0, 0] = pred[0][0]  # 更新收盤價
#             future_features = np.append(future_features[:, 1:], [new_row], axis=1)
        
#         # 模擬未來30天（類似上面的方法）
#         future_features = latest_data.copy()
#         for _ in range(30):
#             pred = model.predict(future_features)
#             trend_30day.append(float(scaler_target.inverse_transform(pred)[0][0]))
            
#             # 更新特徵
#             new_row = future_features[0, -1:].copy()
#             new_row[0, 0] = pred[0][0]
#             future_features = np.append(future_features[:, 1:], [new_row], axis=1)
            
#         # 8. 返回結果
#         result = {
#             "symbol": symbol,
#             "current_price": float(data['Close'].iloc[-1]),
#             "predicted_next_day": float(future_price),
#             "prediction_accuracy": float(accuracy),
#             "sentiment_score": float(data['Sentiment'].iloc[-1]),
#             "trend_5day": trend_5day,
#             "trend_30day": trend_30day,
#             "rmse": float(rmse)
#         }
        
#         return jsonify(result)
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 增加獲取熱門新聞及其情感分析的API
# @stock_app_blueprint.route('/api/stock_news/<symbol>', methods=['GET'])
# @retry_on_429(max_retries=5, initial_delay=2)
# def get_stock_news(symbol):
#     try:
#         # 獲取新聞
#         base_url = f"https://finance.yahoo.com/quote/{symbol}/news"
        
#         response = session.get(base_url)
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         news_data = []
#         news_elements = soup.find_all('div', {'class': 'Py(14px)'})
        
#         for element in news_elements[:10]:  # 最多取前10條新聞
#             try:
#                 # 獲取標題
#                 title_element = element.find('h3')
#                 if not title_element:
#                     continue
#                 title = title_element.get_text().strip()
                
#                 # 獲取連結
#                 link_element = element.find('a')
#                 if link_element and 'href' in link_element.attrs:
#                     link = link_element['href']
#                     if link.startswith('/'):
#                         link = f"https://finance.yahoo.com{link}"
#                 else:
#                     link = "#"
                
#                 # 獲取摘要
#                 summary_element = element.find('p')
#                 summary = summary_element.get_text().strip() if summary_element else ""
                
#                 # 獲取來源和時間
#                 meta_element = element.find('div', {'class': 'C(#959595)'})
#                 source_time = meta_element.get_text().strip() if meta_element else ""
                
#                 # 情感分析
#                 title_sentiment = sid.polarity_scores(title)
#                 summary_sentiment = sid.polarity_scores(summary) if summary else {'compound': 0}
                
#                 # 綜合情感分數 (標題權重0.7，摘要權重0.3)
#                 compound_sentiment = 0.7 * title_sentiment['compound'] + 0.3 * summary_sentiment['compound']
                
#                 # 情感標籤
#                 if compound_sentiment >= 0.05:
#                     sentiment = "正面"
#                     sentiment_color = "#4CAF50"  # 綠色
#                 elif compound_sentiment <= -0.05:
#                     sentiment = "負面"
#                     sentiment_color = "#F44336"  # 紅色
#                 else:
#                     sentiment = "中性"
#                     sentiment_color = "#9E9E9E"  # 灰色
                
#                 news_data.append({
#                     "title": title,
#                     "link": link,
#                     "summary": summary,
#                     "source_time": source_time,
#                     "sentiment": sentiment,
#                     "sentiment_score": compound_sentiment,
#                     "sentiment_color": sentiment_color
#                 })
                
#             except Exception as e:
#                 print(f"Error parsing news element: {e}")
#                 continue
        
#         # 計算整體情感分數
#         if news_data:
#             overall_sentiment = sum(item["sentiment_score"] for item in news_data) / len(news_data)
#         else:
#             overall_sentiment = 0
            
#         # 返回結果
#         return jsonify({
#             "symbol": symbol,
#             "news_count": len(news_data),
#             "overall_sentiment": overall_sentiment,
#             "news": news_data
#         })
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500