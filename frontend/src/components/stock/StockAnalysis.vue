<template>
  <div class="stock-analysis">
    <h1>股票分析</h1>

    <!-- 市場選擇器 -->
    <div class="market-container">
      <market-selector
        :model-value="market"
        @update:model-value="updateMarket"
        @market-change="handleMarketChange"
      />
    </div>

    <!-- 搜尋框 -->
    <div class="search-section">
      <div class="search-box">
        <input
          v-model="stockSymbol"
          :placeholder="
            market === 'US' ? 'Enter US stock symbol...' : '輸入台股代號...'
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
      <button
        v-if="market === 'US'"
        @click="predictStockPrice(stockSymbol)"
        class="predict-button"
      >
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
  import { mapState, mapActions, mapGetters } from "vuex";
  import StockChart from "./StockChart.vue";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";
  import MarketSelector from "../common/MarketSelector.vue";

  export default {
    components: {
      StockChart,
      LoadingSpinner,
      ErrorMessage,
      MarketSelector,
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

        const query = this.stockSymbol.toUpperCase();
        const filtered = this.stockList.filter(
          (stock) =>
            stock &&
            typeof stock === "string" &&
            stock.toUpperCase().startsWith(query)
        );
        return filtered;
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
        // 強制重新獲取股票清單
        this.$store.state.stockApp.categoriesLoaded[this.market] = false;
        await this.fetchStockCategories({ force : true});
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
            await this.fetchStockCategories({ force : true });
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
      ]),
      async fetchStockList() {
        try {
          await this.fetchStockCategories({force : true});
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
        } catch (error) {
          console.error(`載入 ${market} 股票列表失敗:`, error);
        }
      },
      async handleSearch() {
        if (!this.stockSymbol) {
          this.error = "請輸入股票代號";
          return;
        }
        this.resetPredictedPrice();
        this.previousSymbol = this.stockSymbol;

        try {
          const cleanSymbol = this.stockSymbol.split(/\s+/)[0].trim();

          await this.fetchStockChartData(cleanSymbol);
        } catch (error) {
          console.error(`Error fetching ${this.market} stock data:`, error);
        }
      },
      handleInput() {
        if (this.stockSymbol) {
          this.filteredStocks = this.filteredStocksComputed;
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
        if (this.market === "TW" && typeof stock === "string") {
          this.stockSymbol = stock.split(" ")[0];
        } else {
          this.stockSymbol = stock;
        }

        this.showSuggestions = false;
        this.handleSearch();
      },
      navigateToSMAChart(symbol) {
        localStorage.setItem('selectedMarket', this.market);

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
    },
    activated() {
      if (!this.keepData) {
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

  .market-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
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
