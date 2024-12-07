<template>
  <div class="stock-analysis">
    <h1>Stock Data</h1>

    <!-- 股票列表 -->
    <ul class="stock-list">
      <li
        v-for="stock in stockData"
        :key="stock.symbol"
        @click="handleStockClick(stock)"
        class="stock-item"
      >
        {{ stock.symbol }} - ${{ stock.price !== null ? stock.price : 'N/A' }}
      </li>
    </ul>

    <!-- 顯示加載中提示 -->
    <loading-spinner v-if="loading" />
    <error-message v-else-if="error" :message="error" retryable @retry="fetchStockChartData" />

    <!-- 顯示選中的股票 -->
    <div v-if="selectedStock" class="selected-stock">
      <h2>Selected Stock</h2>
      <p>{{ selectedStock.symbol }}: ${{ selectedStock.price }}</p>
      <button @click="navigateToSMAChart(selectedStock.symbol)" class="deep-analysis-button">Deep Analysis</button>
    </div>

    <!-- 股票符號輸入 -->
    <div class="stock-input">
      <input v-model="stockSymbol" placeholder="Enter stock symbol" />
      <button @click="fetchStockChartData(stockSymbol)" class="fetch-button">Fetch Stock Chart</button>
    </div>

    <!-- 預測股票價格 -->
    <div class="stock-predict">
      <button @click="predictStockPrice(stockSymbol)" class="fetch-button">Predict Stock Price</button>
      <p v-if="predictedPrice !== null">Predicted Price: ${{ predictedPrice }}</p>
    </div>

    <!-- 顯示股票圖表 -->
    <stock-chart v-if="chartData" :symbol="stockSymbol" :chartData="chartData" />
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import StockChart from './StockChart.vue';
import LoadingSpinner from '../common/LoadingSpinner.vue';
import ErrorMessage from '../common/ErrorMessage.vue';

export default {
  components: {
    StockChart,
    LoadingSpinner,
    ErrorMessage
  },
  data() {
    return {
      stockSymbol: '',
      selectedStock: null
    };
  },
  computed: {
    ...mapState('stockApp', {
      loading: (state) => state.loading,
      error: (state) => state.error,
      stockData: (state) => state.stockData,
      chartData: (state) => state.chartData,
      predictedPrice: (state) => state.predictedPrice
    })
  },
  methods: {
    ...mapActions('stockApp', ['fetchStockChartData', 'predictStockPrice', 'resetPredictedPrice']),
    async handleStockClick(stock) {
      this.resetPredictedPrice(); // 重置預測價格
      this.selectedStock = stock; // 更新選中的股票
      this.stockSymbol = stock.symbol;
      await this.fetchStockChartData(stock.symbol);
    },
    async fetchStockChartData(symbol) {
      if (!symbol) {
        this.error = 'Please enter a stock symbol';
        return;
      }
      this.stockSymbol = symbol;
      const response = await this.$store.dispatch('stockApp/fetchStockChartData', symbol);
      if (response && response.error) {
        this.error = response.error;
      }
    },
    async predictStockPrice(symbol) {
      if (!symbol) {
        this.error = 'Please enter a stock symbol';
        return;
      }
      await this.$store.dispatch('stockApp/predictStockPrice', symbol);
    },
    navigateToSMAChart(symbol) {
      this.$router.push({ name: 'MovingAvgChart', params: { symbol } });
    }
  },
  mounted() {
    // 預設顯示的股票列表
    this.$store.dispatch('stockApp/fetchStockData');
  }
};
</script>

<style scoped>
.stock-analysis {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.loading {
  color: #007bff;
}

.error {
  color: #ff0000;
}

.stock-list {
  list-style-type: none;
  padding: 0;
}

.stock-item {
  padding: 10px;
  margin: 5px 0;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  cursor: pointer;
  transition: background-color 0.3s;
}

.stock-item:hover {
  background-color: #e9e9e9;
}

.selected-stock {
  margin-top: 20px;
  padding: 10px;
  background-color: #f1f1f1;
  border: 1px solid #ccc;
}

.deep-analysis-button {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.deep-analysis-button:hover {
  background-color: #218838;
}

.stock-input {
  margin-top: 20px;
}

.stock-input input {
  padding: 10px;
  font-size: 16px;
  margin-right: 10px;
}

.fetch-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.fetch-button:hover {
  background-color: #0056b3;
}

.stock-predict {
  margin-top: 20px;
}
</style>