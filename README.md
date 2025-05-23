# Stock Analysis

## 簡介

這是 FinalProject 的專案，用於展示 Vue 和 Flask 的前後端整合，並實現資料的交互。

## 開始使用

這些是設置和運行專案的步驟。

### 1. 創建並激活 Conda 環境

你需要安裝 Conda。可以使用以下命令創建並激活 Conda 環境：

```bash
cd backend/
conda env create -f environment.yml
conda activate flask
```

### 2. 啟動 Flask 伺服器

在後端資料夾內，啟動 Flask 伺服器：

```bash
cd backend/
python app.py
```

Flask 伺服器會在 <http://127.0.0.1:5000> 運行。

### 3. 安裝並運行 Vue 前端

你需要安裝 Node.js 和 npm，然後在前端資料夾中運行：

```bash
cd frontend/
npm install
npm run serve
```

Vue 前端會在 <http://localhost:8080> 運行。

## 前後端整合

前端（Vue）會通過 <http://127.0.0.1:5000/api/data> 跟後端（Flask）進行資料交互。
Flask 預設會提供 API，並允許 CORS（跨源資源共享），這樣 Vue 前端就能夠從不同端口的伺服器請求資料。

## 技術栈

### 前端

Vue 3
Vue CLI
axios 用於 HTTP 請求

### 後端

Flask
Flask-CORS 用於處理跨域請求
pandas、numpy 用於資料處理

## 開發者設置

### 安裝 MongoDB

#### Windows

1. 前往 [MongoDB 下載頁面](https://www.mongodb.com/try/download/community) 也可找尋影片跟著做
2. 選擇 Windows 版本並下載安裝程式 (.msi)
3. 執行安裝程式並按照步驟安裝
4. 建議選擇 "Complete" 安裝，並安裝 MongoDB Compass (圖形化管理工具)
5. 安裝完成後，MongoDB 服務會自動啟動
   - MongoDB 默認執行於 `localhost:27017`
   - 數據存儲在 `C:\Files\MongoDB\Server\<version>\data\db`
6. 創建 "stock" 資料庫
    1. 連接到 MongoDB (默認連接 mongodb://localhost:27017)
    2. 點擊 "Create Database"
    3. 輸入資料庫名稱 "stock"
    4. 輸入初始集合名稱 (例如 "users" 或 "stocks")
    5. 點擊 "Create Database"

#### macOS

1. 使用 Homebrew 安裝: (這個我不熟，請自己去找教學)

   ```bash
   brew tap mongodb/brew
   brew install mongodb-community@6.0
   ```

### 1. 克隆專案

首先，你需要將專案克隆到本地：

```bash
git clone https://github.com/XiaoWang1212/data_visual.git
cd data_visual
```

### 2. 安裝後端環境

在後端資料夾內創建並激活 Conda 環境：

```bash
cd backend/
conda env create -f environment.yml
conda activate flask
conda install TA_Lib-0.4.28-cp312-cp312-win_amd64.whl
```

### 3. 安裝前端依賴

安裝 Node.js 和 npm，並在前端資料夾安裝依賴：

```bash
cd .. # 退回到跟根目錄
cd frontend/
npm install
```

### 4. 開啟網頁

```bash
cd .. # 退回到跟根目錄
npm install
```

#### 以後要執行就跑

```bash
npm start
```

## Git 教學

### 1. 檢查檔案狀態

修改過程中，可以使用 git status 命令查看有沒有更改的文件：

```bash
git status
```

### 2. 將更改添加到 Git 追蹤清單

修改完畢後，使用 git add 命令將更改的文件加入 Git 追蹤：

```bash
git add .
```

這會將所有改動的檔案加入暫存區。

### 3. 提交更改

然後用 git commit 提交更改，並寫下有意義的提交訊息：

```bash
git commit -m "描述你修改的內容"
```

### 4. 推送到 GitHub

提交後，可以將更改推送到 GitHub 上的遠端儲存庫：

```bash
git push origin main
```

### 5. 拉取最新更改

如果他們在開發過程中，其他人也有推送新更改，需要定期使用 git pull 命令來更新本地資料夾：

```bash
git pull origin main
```

### 6. 處理衝突

如果多人同時編輯相同的文件，可能會發生合併衝突。當遇到衝突時 Git 會標記出衝突部分，需要手動修改並重新提交。

常見問題

1. 啟動 Flask 伺服器時出現錯誤
   請確保你的 Conda 環境已經成功激活，並且沒有其他應用佔用了 5000 端口。你可以在 app.py 中更改端口配置

### PS
Remove environment

```
conda deactivate
conda remove --name flask --all
```