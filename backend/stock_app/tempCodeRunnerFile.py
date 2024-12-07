import requests
import pandas as pd
import os
from io import StringIO

# 台灣證券交易所 上市公司清單的 URL
url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"

# 發送 GET 請求
response = requests.get(url)
response.encoding = 'big5'  # TWSE 頁面使用 Big5 編碼

# 使用 Pandas 解析 HTML 表格
tables = pd.read_html(StringIO(response.text))
stocks_table = tables[0]  # 第一個表格是我們需要的

# 整理數據（刪除無用列、重新命名欄位）
stocks_table.columns = stocks_table.iloc[0]
stocks_table = stocks_table[1:]  # 刪除第一行標題
stocks_table = stocks_table.dropna(how='all', axis=1)  # 刪除空白列

# 分離有價證券代號及名稱
stocks_table[['有價證券代號', '有價證券名稱']] = stocks_table['有價證券代號及名稱'].str.split('\u3000', expand=True)

# 過濾出 TWSE 上市公司
stocks_table = stocks_table[stocks_table["市場別"].str.contains("上市")]

# 選擇需要的欄位
stocks_table = stocks_table[['有價證券代號', '有價證券名稱', '國際證券辨識號碼(ISIN Code)', '上市日', '市場別', '產業別']]

# 確保檔案儲存路徑存在
output_dir = os.path.join(os.getcwd(), "output")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "twse_listed_stocks.csv")

# 儲存為 CSV
stocks_table.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"台灣上市股票清單已儲存為 {output_file}")