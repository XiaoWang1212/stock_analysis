<template>
  <div class="stock-analysis">
    <h1>股票分析</h1>

    <!-- 搜尋框 -->
    <div class="search-section">
      <div class="search-box">
        <input
          v-model="stockSymbol"
          placeholder="輸入股票代號..."
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
            class="suggestion-item"
          >
            {{ stock }}
          </div>
        </div>
        <button @click="handleSearch" class="search-button">搜尋</button>
      </div>

      <button
        v-if="stockSymbol"
        @click="navigateToSMAChart(stockSymbol)"
        class="analysis-button"
      >
        技術分析
      </button>
    </div>

    <!-- 載入中和錯誤提示 -->
    <loading-spinner v-if="loading" />
    <error-message v-else-if="error" :message="error" @retry="handleSearch" />

    <!-- 預測區塊 -->
    <div v-if="chartData" class="predict-section">
      <button @click="predictStockPrice(stockSymbol)" class="predict-button">
        預測股價
      </button>
      <p v-if="predictedPrice !== null" class="predicted-price">
        預測價格: ${{ predictedPrice }}
      </p>
    </div>

    <!-- 股票圖表 -->
    <div class="stock-chart-container">
      <stock-chart
        v-if="chartData"
        :symbol="stockSymbol"
        :chartData="chartData"
      />
    </div>
  </div>
</template>

<script>
  import { mapState, mapActions } from "vuex";
  import StockChart from "./StockChart.vue";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";

  export default {
    components: {
      StockChart,
      LoadingSpinner,
      ErrorMessage,
    },
    props: {
      symbol: {
        type: String,
        default: "",
      },
    },
    data() {
      return {
        stockSymbol: this.symbol || "",
        previousSymbol: "",
        stockList: [],
        showSuggestions: false,
        filteredStocks: [],
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        error: (state) => state.error,
        chartData: (state) => state.chartData,
        predictedPrice: (state) => state.predictedPrice,
      }),
    },
    watch: {
      $route(to, from) {
        if (from.name === "MovingAvgChart" && to.name === "StockAnalysis") {
          const symbol = to.params.symbol;
          const keepData = to.query.keepData === "true";

          if (symbol) {
            this.stockSymbol = symbol;
            this.previousSymbol = symbol;

            if (keepData && this.chartData) {
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
    created() {
      this.fetchStockList();

      // 如果有 symbol prop，初始化搜索
      if (this.symbol) {
        this.stockSymbol = this.symbol;
        this.handleSearch();
      }

      // 檢查 query 參數
      const keepData = this.$route.query.keepData === "true";
      if (!keepData && this.chartData) {
        this.resetChartData();
      }
    },
    methods: {
      ...mapActions("stockApp", [
        "fetchStockChartData",
        "predictStockPrice",
        "resetPredictedPrice",
        "resetChartData",
      ]),
      async fetchStockList() {
        try {
          const response = await fetch(
            "http://127.0.0.1:5000/stock_app/api/categories"
          );
          const data = await response.json();
          this.stockList = data.map((item) => item.ticker).filter(Boolean);
        } catch (error) {
          console.error("Error fetching stock list:", error);
          this.stockList = [];
        }
      },
      async handleSearch() {
        if (!this.stockSymbol) {
          this.error = "請輸入股票代號";
          return;
        }
        this.resetPredictedPrice();
        this.previousSymbol = this.stockSymbol;
        await this.fetchStockChartData(this.stockSymbol);
      },
      handleInput() {
        if (this.stockSymbol) {
          const query = this.stockSymbol.toUpperCase();
          this.filteredStocks = this.stockList.filter((stock) =>
            stock.startsWith(query)
          );
          this.showSuggestions = this.filteredStocks.length > 0;

          // 如果用戶修改了搜索內容（與上次搜索不同），則清除圖表
          if (this.previousSymbol && this.stockSymbol !== this.previousSymbol) {
            this.resetChartData();
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
        this.stockSymbol = stock;
        this.showSuggestions = false;
        this.handleSearch();
      },
      navigateToSMAChart(symbol) {
        this.$router.push({ name: "MovingAvgChart", params: { symbol } });
      },
      fixLayout() {
        const container = document.querySelector(".stock-analysis");
        if (container) {
          container.style.display = "none";
          container.offsetHeight;
          container.style.display = "";
        }
      },
    },
    activated() {
      if (this.$route.query.keepData !== "true") {
        this.resetChartData();
      }
    },
    mounted() {
      console.log("組件掛載，當前股票代號:", this.stockSymbol);
    },
    beforeUnmount() {
      if (!this.$route.name || !["MovingAvgChart"].includes(this.$route.name)) {
        this.resetChartData();
      }
    },
  };
</script>

<style scoped>
  .stock-analysis {
    display: flex;
    flex-direction: column;
    padding: 30px;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    box-sizing: border-box;
  }

  .search-section {
    display: flex;
    gap: 20px;
    justify-content: center;
    align-items: center;
    margin-bottom: 30px;
    width: 100%;
    max-width: 100%;
  }

  .search-box {
    display: flex;
    gap: 10px;
    flex: 0 1 auto;
    width: 60%;
    max-width: 400px;
    position: relative;
  }

  .search-input {
    flex: 1;
    padding: 12px;
    font-size: 16px;
    border: 2px solid #ddd;
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
  .analysis-button,
  .predict-button {
    padding: 12px 24px;
    font-size: 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .search-button {
    background-color: #4a90e2;
    color: white;
  }

  .search-button:hover {
    background-color: #357abd;
  }

  .search-box {
    position: relative;
  }

  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    max-height: 150px;
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

  .analysis-button {
    background-color: #28a745;
    color: white;
  }

  .analysis-button:hover {
    background-color: #218838;
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

  .stock-chart-container {
    flex: 0 1 auto;
    width: 60%;
    max-width: 600px;
    margin: 0 auto;
    overflow-x: hidden;
  }

  h1 {
    color: #2c3e50;
    margin-bottom: 30px;
  }
</style>
