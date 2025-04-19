<template>
  <div class="wma-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer"></div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { mapState, mapActions } from "vuex";
  import { nextTick } from "vue";

  export default {
    props: {
      symbol: {
        type: String,
        required: true,
      },
      market: {
        type: String,
        required: true,
      },
      stockName: {
        type: String,
        default: "",
      },
    },
    data() {
      return {
        chartData: null,
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        error: (state) => state.error,
        twStockNameMap: (state) => state.twStockNameMap,
      }),

      displayName() {
        // 如果已經從父組件接收了名稱，則使用它
        if (this.stockName) {
          return this.stockName;
        }

        // 如果是台股
        if (this.market === "TW" && this.twStockNameMap) {
          return this.twStockNameMap[this.symbol] || "";
        }

        return ""; // 預設空字串
      },
    },
    watch: {
      symbol: "fetchChartData",
      market: "fetchChartData",
    },
    methods: {
      ...mapActions("stockApp", [
        "fetchSMAChartData",
        "generateTwStockNameMap",
      ]),
      async fetchChartData() {
        try {
          this.chartData = null;

          // 如果是台股且沒有名稱映射，先獲取名稱映射
          if (
            this.market === "TW" &&
            (!this.twStockNameMap ||
              Object.keys(this.twStockNameMap).length === 0)
          ) {
            await this.generateTwStockNameMap();
          }

          await this.fetchSMAChartData(this.symbol, this.market);

          if (!this.error) {
            this.chartData = this.$store.state.stockApp.chartData;
            await nextTick();
            this.renderChart();
          }
        } catch (error) {
          console.error(`獲取 EMA 圖表數據時發生錯誤:`, error);
        }
      },
      async renderChart() {
        await nextTick(); // 確保 DOM 更新完成
        const {
          dates,
          close_prices,
          high_prices,
          low_prices,
          open_prices,
          wma_5,
          wma_20,
        } = this.chartData;

        const traceCandlestick = {
          x: dates,
          close: close_prices,
          high: high_prices,
          low: low_prices,
          open: open_prices,
          type: "candlestick",
          name: "Candlestick",
          increasing: { line: { color: "#FF0000" }, fillcolor: "#FFCCCC" },
          decreasing: { line: { color: "#008000" }, fillcolor: "#CCFFCC" },
        };

        const traceWMA5 = {
          x: dates,
          y: wma_5,
          type: "scatter",
          mode: "lines",
          name: "WMA 5",
          line: { color: "black" },
        };

        const traceWMA20 = {
          x: dates,
          y: wma_20,
          type: "scatter",
          mode: "lines",
          name: "WMA 20",
          line: { color: "blue" },
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` (${this.displayName})`;
        }
        chartTitle += ` WMA Chart(權重)`;

        const layout = {
          title: chartTitle,
          xaxis: { title: "Date" },
          yaxis: { title: "Price" },
          showlegend: true,
          hovermode: "x unified",
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceCandlestick, traceWMA5, traceWMA20],
          layout
        );
      },
    },
    async mounted() {
      if (
        this.market === "TW" &&
        (!this.twStockNameMap || Object.keys(this.twStockNameMap).length === 0)
      ) {
        try {
          await this.generateTwStockNameMap();
        } catch (error) {
          console.error("獲取台股名稱映射時出錯:", error);
        }
      }

      this.fetchChartData();
    },
    beforeUnmount() {
      // 清理圖表資源
      if (this.$refs.chartContainer) {
        Plotly.purge(this.$refs.chartContainer);
      }
    },
  };
</script>

<style scoped>
  .wma-chart {
    margin: 20px 0;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    background-color: #fff;
  }

  h3 {
    margin-top: 0;
    color: #333;
    font-size: 1.2rem;
    text-align: center;
    margin-bottom: 15px;
  }

  .loading {
    color: #007bff;
    text-align: center;
    padding: 20px;
    font-style: italic;
  }

  .error {
    color: #dc3545;
    text-align: center;
    padding: 15px;
    margin: 10px 0;
    background-color: #f8d7da;
    border-radius: 4px;
  }
</style>
