<template>
  <div class="sma-chart">
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
        "setCurrentMarket",
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
          sma_5,
          sma_20,
          sma_60,
        } = this.chartData;

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const traceCandlestick = {
          x: indices,
          close: close_prices,
          high: high_prices,
          low: low_prices,
          open: open_prices,
          type: "candlestick",
          name: "Candlestick",
          increasing: { line: { color: "#FF2D2D" }, fillcolor: "#FFCCCC" },
          decreasing: { line: { color: "#02DF82" }, fillcolor: "#CCFFCC" },
          text: dates,
        };

        const traceSMA5 = {
          x: indices,
          y: sma_5,
          type: "scatter",
          mode: "lines",
          name: "SMA 5",
          line: { color: "#FF79BC" },
        };

        const traceSMA20 = {
          x: indices,
          y: sma_20,
          type: "scatter",
          mode: "lines",
          name: "SMA 20",
          line: { color: "#66B3FF" },
        };

        const traceSMA60 = {
          x: indices,
          y: sma_60,
          type: "scatter",
          mode: "lines",
          name: "SMA 60",
          line: { color: "#9F35FF" },
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` - ${this.displayName}`;
        }
        chartTitle += ` SMA Chart - 簡單`;

        const layout = {
          title: {
            text: chartTitle,
            font: {
              color: 'white',
            }
          },
          legend: {
            font: {
              color: "#BEBEBE"
            },
          },
          xaxis: { title: "Date", color: '#BEBEBE', gridcolor: '#7B7B7B'},
          yaxis: { title: "Price", color: '#BEBEBE', gridcolor: '#7B7B7B'},
          showlegend: true,
          hovermode: "x unified", // 提供更友好的 hover 效果
          hoverlabel: {
            bgcolor: "#FFF",
            bordercolor: "#999",
            font: { size: 12 },
          },
          paper_bgcolor: '#4F4F4F',
          plot_bgcolor: '#4F4F4F',
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceCandlestick, traceSMA5, traceSMA20, traceSMA60],
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
    created() {
      this.setCurrentMarket(this.market);
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
  .sma-chart {
    border-radius: 8px;
    border-top: 2px solid #7B7B7B;
    border-bottom: 2px solid #7B7B7B;
    background-color: #4F4F4F;
  }

  h3 {
    margin-top: 0;
    color: white;
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
    color: black;
    text-align: center;
    padding: 15px;
    margin: 10px 0;
    background-color: #f8d7da;
    border-radius: 4px;
  }
</style>
