<template>
  <div class="stock-analysis">

    <!-- 市場選擇器 -->
    <div class="market-container" v-if="showMarketSelector">
      <market-selector
        :model-value="market"
        @update:model-value="updateMarket"
        @market-change="handleMarketChange"
      />
    </div>

    <div class="analysis-button-flame">
      <button
        v-if="stockSymbol"
        @click="navigateToSMAChart(stockSymbol)"
        class="analysis-button"
      >
        技術分析
      </button>
    </div>

    <!-- 預測區塊 -->
    <div v-if="chartData" class="predict-section">
      <button
        @click="togglePredictionView"
        class="predict-button"
        :class="{ active: showPrediction }"
      >
        {{ showPrediction ? "隱藏預測" : "AI智能預測" }}
      </button>

      <transition name="fade">
        <div v-if="showPrediction" class="prediction-container">
          <div class="prediction-header">
            <h3>LSTM預測</h3>
            <span class="tech-badge">Deep Learning</span>
          </div>

          <lstm-prediction-chart
            v-if="showPrediction"
            :symbol="stockSymbol"
            :market="market"
          />
        </div>
      </transition>
    </div>

      <!-- 載入中和錯誤提示 -->
      <loading-spinner v-if="loading" class="loading-spinner"/>
      <error-message v-else-if="error" :message="error" @retry="handleSearch" />

      <!-- 股票圖表 -->
      <div class="stock-chart-container">
        <stock-chart
          v-if="chartData && !showPrediction"
          :symbol="stockSymbol"
          :chartData="chartData"
        />
      </div>
  </div>

  <!-- 搜尋框 -->
  <div class="search-section">
    <div class="search-box">
      <input
        v-model="stockSymbol"
        :placeholder="
          market === 'US'
            ? 'Enter US stock symbol...'
            : '輸入台股代號或中文名稱...'
        "
        class="search-input"
        @input="handleInput"
        @keyup.enter="handleSearch"
      />
      <div
        v-if="showSuggestions && filteredStocks.length"
        class="suggestions"
      >
        <div
          v-for="stock in filteredStocks"
          :key="stock"
          @click="selectStock(stock)"
          :class="['suggestion-item', { 'us-stock': market === 'US' }]"
        >
          <template v-if="market === 'TW' && stock.includes(' ')">
            <span class="stock-name">{{ getStockName(stock) }}</span>
            <span class="stock-code">{{ getStockCode(stock) }}</span>
          </template>
          <template v-else>
            <span class="us-symbol">{{ stock }}</span>
          </template>
        </div>
      </div>
      <button @click="handleSearch" class="search-button">搜尋</button>

      <!--
      <button
        v-if="stockSymbol"
        @click="navigateToSMAChart(stockSymbol)"
        class="analysis-button"
      >
        技術分析
      </button>
      -->
    </div>
  </div>

</template>

<script>
  import { mapState, mapActions, mapGetters } from "vuex";
  import StockChart from "./StockChart.vue";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";
  import MarketSelector from "../common/MarketSelector.vue";
  import LstmPredictionChart from "./LstmPredictionChart.vue";

  export default {
    components: {
      StockChart,
      LoadingSpinner,
      ErrorMessage,
      MarketSelector,
      LstmPredictionChart,
    },
    props: {
      symbol: {
        type: String,
        default: "",
      },
      keepData: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        stockSymbol: this.symbol || "",
        previousSymbol: "",
        showSuggestions: false,
        filteredStocks: [],
        switchingMarket: false,
        showMarketSelector: false, // 測試用
        showPrediction: false,
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        error: (state) => state.error,
        chartData: (state) => state.chartData,
        predictedPrice: (state) => state.predictedPrice,
      }),
      ...mapGetters("stockApp", ["stockList", "currentMarket"]),
      market: {
        get() {
          return this.currentMarket;
        },
        set(value) {
          this.setCurrentMarket(value);
        },
      },
      filteredStocksComputed() {
        // 如果沒有股票清單或不是數組，則返回空數組
        if (!this.stockList || !Array.isArray(this.stockList)) {
          console.warn(`股票清單無效: ${JSON.stringify(this.stockList)}`);
          return [];
        }

        // 如果沒有輸入搜索詞，則返回空數組
        if (!this.stockSymbol) {
          return [];
        }

        const query = this.stockSymbol.trim().toLowerCase();
        let filteredStocks = [];

        if (this.market === "TW") {
          const twStockNameMap =
            this.$store.state.stockApp.twStockNameMap || {};

          // 1. 先按照代號搜尋
          const codeMatches = this.stockList.filter(
            (stock) => stock && stock.toLowerCase().startsWith(query)
          );

          // 為匹配的代號添加中文名稱
          filteredStocks = codeMatches.map((code) => {
            const name = twStockNameMap[code];
            return name ? `${code} ${name}` : code;
          });

          // 2. 如果輸入包含中文，搜尋股票名稱
          if (/[\u4e00-\u9fa5]/.test(query)) {
            Object.entries(twStockNameMap).forEach(([code, name]) => {
              if (name && name.toLowerCase().includes(query)) {
                const formattedStock = `${code} ${name}`;
                // 避免重複添加
                if (!filteredStocks.some((s) => s.startsWith(code + " "))) {
                  filteredStocks.push(formattedStock);
                }
              }
            });
          }

          return filteredStocks.slice(0, 10);
        } else {
          // 美股搜索邏輯
          const upperQuery = query.toUpperCase();
          return this.stockList
            .filter(
              (stock) =>
                stock &&
                typeof stock === "string" &&
                stock.toUpperCase().startsWith(upperQuery)
            )
            .slice(0, 20);
        }
      },
    },
    watch: {
      $route(to, from) {
        if (from.name === "MovingAvgChart" && to.name === "StockAnalysis") {
          if (to.params.symbol) {
            this.stockSymbol = to.params.symbol;
            this.previousSymbol = to.params.symbol;

            // 設置正確的市場
            if (to.params.market) {
              this.market = to.params.market;
            }

            if (to.query.keepData && this.chartData) {
              this.$nextTick(() => {
                this.fixLayout();
              });
            } else {
              this.handleSearch();
            }
          }
        }
      },
      symbol(newSymbol) {
        if (newSymbol && newSymbol !== this.stockSymbol) {
          this.stockSymbol = newSymbol;
          this.handleSearch();
        }
      },
    },
    async created() {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const marketParam = urlParams.get("market");
        const symbolParam = urlParams.get("symbol");

        if (!symbolParam && !this.symbol && this.$route.path === "/stock-app") {
          this.resetChartData();
          this.previousSymbol = "";
          this.stockSymbol = "";
          this.showPrediction = false;
        }

        if (marketParam) {
          const normalizedMarket = marketParam.toUpperCase();
          if (normalizedMarket === "TW" || normalizedMarket === "US") {
            this.market = normalizedMarket;

            this.setCurrentMarket(normalizedMarket);
          }
        }

        this.$store.state.stockApp.categoriesLoaded[this.market] = false;
        await this.fetchStockCategories({ force: true });
      } catch (error) {
        console.error(
          `載入${this.market === "US" ? "美股" : "台股"}列表失敗:`,
          error
        );
      }

      // 如果有 symbol prop，初始化搜索
      if (this.symbol) {
        this.stockSymbol = this.symbol;
        this.handleSearch();
      }

      // 檢查 query 參數
      const urlParams = new URLSearchParams(window.location.search);
      const symbolParam = urlParams.get("symbol");
      const marketParam = urlParams.get("market");

      if (marketParam) {
        const normalizedMarket = marketParam.toUpperCase();
        if (normalizedMarket !== this.market) {
          this.market = normalizedMarket;

          // 市場變更後重新獲取股票列表
          try {
            await this.fetchStockCategories({ force: true });
          } catch (error) {
            console.error(`載入${this.market}股票列表失敗:`, error);
          }
        }
      }

      let symbolToSearch = null;

      if (this.symbol) {
        symbolToSearch = this.symbol;
      } else if (symbolParam) {
        symbolToSearch = symbolParam;
      }

      if (symbolToSearch) {
        this.stockSymbol = symbolToSearch;
        await this.handleSearch();
      }
    },
    methods: {
      ...mapActions("stockApp", [
        "fetchStockCategories",
        "fetchStockChartData",
        "predictStockPrice",
        "resetPredictedPrice",
        "resetChartData",
        "setCurrentMarket",
        "generateTwStockNameMap",
      ]),
      async fetchStockList() {
        try {
          await this.fetchStockCategories({ force: true });
        } catch (error) {
          console.error("Error fetching stock list:", error);
        }
      },
      async handleMarketChange(market) {
        // 先重置相關狀態
        this.resetChartData();
        this.stockSymbol = "";
        this.previousSymbol = "";
        this.showSuggestions = false;
        this.filteredStocks = [];

        // 更新市場設置
        this.updateMarket(market);

        // 強制重新獲取股票列表，不使用緩存
        try {
          // 先將 categoriesLoaded 重置為 false，這樣可以強制重新獲取
          if (this.$store.state.stockApp.categoriesLoaded) {
            // 直接修改 store 中的 categoriesLoaded 狀態
            this.$store.state.stockApp.categoriesLoaded[market] = false;
          }

          await this.fetchStockCategories({ force: true });

          if (market === "TW") {
            this.generateTwStockNameMap();
          }
        } catch (error) {
          console.error(`載入 ${market} 股票列表失敗:`, error);
        }
      },
      async handleSearch() {
        if (!this.stockSymbol) {
          this.error = "請輸入股票代號或名稱";
          return;
        }

        this.resetPredictedPrice();

        // 處理可能的中文名稱搜索
        let symbolToSearch = this.stockSymbol.trim();

        if (this.market === "TW") {
          const twStockNameMap =
            this.$store.state.stockApp.twStockNameMap || {};

          // 如果包含中文，查找對應的股票代號
          if (/[\u4e00-\u9fa5]/.test(symbolToSearch)) {
            const foundEntry = Object.entries(twStockNameMap).find(
              ([name]) => name && name.includes(symbolToSearch)
            );

            if (foundEntry) {
              symbolToSearch = foundEntry[0]; // 使用股票代號
              console.log(
                `找到中文名稱 "${this.stockSymbol}" 對應的股票代號: ${symbolToSearch}`
              );
            }
          } else if (symbolToSearch.includes(" ")) {
            // 如果是 "代號 名稱" 格式，提取代號部分
            symbolToSearch = symbolToSearch.split(" ")[0].trim();
          }
        } else {
          // 美股處理：去除可能的空格等
          symbolToSearch = symbolToSearch.split(/\s+/)[0].trim();
        }

        this.previousSymbol = symbolToSearch;

        try {
          await this.fetchStockChartData(symbolToSearch);
        } catch (error) {
          console.error(`Error fetching ${this.market} stock data:`, error);
        }
      },
      handleInput() {
        if (this.stockSymbol) {
          this.detectInputTypeAndSwitchMarket();

          if (!this.switchingMarket) {
            // 防護措施：只有在 stockList 可用時才計算過濾結果
            if (this.stockList && Array.isArray(this.stockList)) {
              this.filteredStocks = this.filteredStocksComputed;
              this.showSuggestions = this.filteredStocks.length > 0;
            } else {
              this.filteredStocks = [];
              this.showSuggestions = false;
            }
          }

          // 如果用戶修改了搜索內容（與上次搜索不同），則清除圖表
          if (this.chartData) {
            this.resetChartData();
          }

          if (this.showPrediction) {
            this.showPrediction = false;
          }
        } else {
          this.showSuggestions = false;
          this.filteredStocks = [];

          if (this.previousSymbol) {
            this.resetChartData();
            this.previousSymbol = ""; // 重置上一次搜索的符號
          }
        }
      },
      selectStock(stock) {
        if (this.market === "TW" && typeof stock === "string") {
          this.stockSymbol = this.getStockCode(stock);
        } else {
          this.stockSymbol = stock;
        }

        this.showSuggestions = false;
        this.handleSearch();
      },
      navigateToSMAChart(symbol) {
        localStorage.setItem("selectedMarket", this.market);

        this.$router.push({
          name: "MovingAvgChart",
          params: { symbol },
          query: { market: this.market },
        });
      },
      updateMarket(market) {
        this.market = market;
      },
      fixLayout() {
        const container = document.querySelector(".stock-analysis");
        if (container) {
          container.style.display = "none";
          container.offsetHeight;
          container.style.display = "";
        }
      },
      getStockCode(stock) {
        return stock.split(" ")[0];
      },
      getStockName(stock) {
        return stock.split(" ").slice(1).join(" ");
      },
      detectInputTypeAndSwitchMarket() {
        const input = this.stockSymbol.trim();

        // 檢測是否包含中文
        const containsChinese = /[\u4e00-\u9fa5]/.test(input);

        // 檢測是否以數字開頭（台股特徵）
        const startsWithDigit = /^\d+/.test(input);

        // 檢測是否需要切換市場
        let targetMarket = null;

        // 如果包含中文或以數字開頭，應該是台股
        if ((containsChinese || startsWithDigit) && this.market !== "TW") {
          targetMarket = "TW";
        }
        // 如果以英文字母開頭，應該是美股
        else if (
          !containsChinese &&
          !startsWithDigit &&
          /^[A-Za-z]/.test(input) &&
          this.market !== "US"
        ) {
          targetMarket = "US";
        }

        if (targetMarket) {
          this.performMarketSwitch(targetMarket);
        }
      },
      async performMarketSwitch(targetMarket) {
        this.switchingMarket = true;

        // 先清空建議列表，避免錯誤
        this.filteredStocks = [];
        this.showSuggestions = false;

        if (this.$store.state.stockApp.categoriesLoaded) {
          this.$store.state.stockApp.categoriesLoaded[targetMarket] = false;
        }

        // 切換市場
        this.market = targetMarket;

        // 獲取新市場的股票列表
        await this.fetchStockCategories({ force: true });

        // 如果是台股，生成名稱映射
        if (targetMarket === "TW") {
          await this.generateTwStockNameMap();
        }

        setTimeout(() => {
          this.switchingMarket = false;

          try {
            this.filteredStocks = this.filteredStocksComputed;
            this.showSuggestions = this.filteredStocks.length > 0;
          } catch (err) {
            console.error("更新建議列表時出錯:", err);
          }
        }, 100);
      },
      togglePredictionView() {
        this.showPrediction = !this.showPrediction;
      },
    },
    activated() {
      if (!this.keepData) {
        this.resetChartData();
      }
    },
    mounted() {
      this.showPrediction = false;
    },
    beforeUnmount() {
      if (!this.$route.name || !["MovingAvgChart"].includes(this.$route.name)) {
        this.resetChartData();
        this.showPrediction = false;
      }
    },
  };
</script>

<style scoped>
  .stock-analysis {
    padding: 30px;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .market-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }

  .search-section {
    display: flex;
    gap: 20px;
    justify-content: end;
    align-items: start;
    margin-bottom: 30px;
    width: 100%;
    max-width: 100%;
  }

  .search-box {
    display: flex;
    gap: 10px;
    flex: 0 1 auto;
    width: 100%;
    max-width: 400px;
    position: relative;
    right: 5%;
  }

  .search-input {
    flex: 1;
    padding: 12px;
    font-size: 16px;
    border: 2px solid #66B3FF;
    border-radius: 6px;
    transition: border-color 0.3s;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }

  .search-input:focus {
    outline: none;
    border-color: #4a90e2;
  }

  .search-button,
  .analysis-button {
    padding: 12px 24px;
    font-size: 16px;
    font-weight: bold;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .search-button {
    background-color: #66B3FF;
    color: white;
  }

  .search-button:hover {
    background-color: #2894FF;
  }

  .search-box {
    padding: 30px;
    position: relative;
  }

  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 5%;
    width: 100%;
    max-height: 250px;
    overflow-y: auto;
    background: white;
    border: 1px solid #ddd;
    border-radius: 0 0 4px 4px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    margin-top: 5px;
    scrollbar-width: thin;
    scrollbar-color: #888 #f1f1f1;
  }

  .suggestion-item {
    padding: 12px 15px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 48px;
    box-sizing: border-box;
  }

  .suggestion-item.us-stock {
    justify-content: center;
  }

  .suggestion-item:last-child {
    border-bottom: none;
  }

  .suggestion-item:hover {
    background-color: #f5f5f5;
  }

  /* 添加滾動條樣式 */
  .suggestions::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  .suggestions::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .suggestions::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }

  .suggestions::-webkit-scrollbar-thumb:hover {
    background: #555;
  }

  .analysis-button-flame{
    display: flex;
    justify-content: center;
  }

  .analysis-button {
    background-color: #66B3FF;
    color: white;
    width: 120px;
  }

  .analysis-button:hover {
    background-color: #2894FF;
  }

  .predict-section {
    margin: 20px 0;
  }

  .predict-button {
    background-color: #17a2b8;
    color: white;
  }

  .predict-button:hover {
    background-color: #138496;
  }

  .predicted-price {
    margin-top: 10px;
    font-size: 18px;
    color: #28a745;
    font-weight: bold;
  }

  .loading-spinner{
    height: 60vh;
  }

  .stock-chart-container {
    flex: 0 1 auto;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    overflow-x: hidden;
  }

  .stock-code {
    font-weight: bold;
    color: #666;
    margin-right: 10px;
    flex-shrink: 0;
    min-width: 50px;
  }

  .stock-name {
    font-weight: bold;
    color: #333;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .us-symbol {
    font-weight: bold;
    font-size: 1.1rem;
    color: #333;
  }

  h1 {
    color: #2c3e50;
    margin-bottom: 30px;
  }

  .predict-button {
    background-color: #17a2b8;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: block;
    margin: 0 auto;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .predict-button:hover {
    background-color: #138496;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .predict-button.active {
    background-color: #dc3545;
  }

  .predict-button.active:hover {
    background-color: #c82333;
  }

  .prediction-container {
    margin-top: 20px;
    padding: 20px;
    border-radius: 8px;
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    max-width: 100%;
  }

  .prediction-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 10px;
  }

  .prediction-header h3 {
    margin: 0;
    color: #343a40;
    font-size: 18px;
  }

  .tech-badge {
    background-color: #6610f2;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.5s, transform 0.5s;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
    transform: translateY(-20px);
  }
</style>
