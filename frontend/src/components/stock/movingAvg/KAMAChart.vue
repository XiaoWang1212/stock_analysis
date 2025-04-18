<template>
  <div class="kama-chart">
    <h3>{{ symbol }} KAMA Chart</h3>
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
    },
    data() {
      return {
        chartData: null,
        isInitialLoad: true,
        localError: null,
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        storeError: (state) => state.error,
        storeChartData: (state) => state.chartData,
      }),

      error() {
        return this.storeError || this.localError;
      },
    },
    watch: {
      symbol() {
        this.fetchChartData();
      },
      market() {
        this.fetchChartData();
      },
      storeChartData: {
        handler(newData) {
          if (newData && !this.chartData) {
            this.processChartData(newData);
          }
        },
        deep: true,
      },
    },
    methods: {
      ...mapActions("stockApp", ["fetchSMAChartData", "setCurrentMarket"]), 

      async fetchChartData() {
        try {
          this.chartData = null;
          this.localError = null;

          this.setCurrentMarket(this.market);

          await this.fetchSMAChartData(this.symbol);

          if (!this.storeError && this.storeChartData) {
            this.processChartData(this.storeChartData);
          } else if (this.storeError) {
            console.error(
              `獲取 ${this.symbol} 的 EMA 數據出錯: ${this.storeError}`
            );
          }
        } catch (error) {
          console.error(`獲取 EMA 圖表數據時發生錯誤:`, error);
          this.localError = `獲取圖表數據失敗: ${error.message}`;
        }
      },
      processChartData(data) {
        try {
          if (!data || !data.dates) {
            throw new Error("圖表數據不完整或格式不正確");
          }

          this.chartData = data;

          this.$nextTick(() => {
            this.renderChart();
          });
        } catch (error) {
          console.error("處理圖表數據時出錯:", error);
          this.localError = `處理圖表數據失敗: ${error.message}`;
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
          kama_5,
          kama_20,
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

        const traceKAMA5 = {
          x: dates,
          y: kama_5,
          type: "scatter",
          mode: "lines",
          name: "KAMA 5",
          line: { color: "black" },
        };

        const traceKAMA20 = {
          x: dates,
          y: kama_20,
          type: "scatter",
          mode: "lines",
          name: "KAMA 20",
          line: { color: "blue" },
        };

        const layout = {
          title: `${this.symbol} KAMA Chart(考夫曼自適應)`,
          xaxis: { title: "Date" },
          yaxis: { title: "Price" },
          showlegend: true,
          hovermode: "x unified", // 提供更友好的 hover 效果
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceCandlestick, traceKAMA5, traceKAMA20],
          layout
        );
      },
    },
    mounted() {
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
  .kama-chart {
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
