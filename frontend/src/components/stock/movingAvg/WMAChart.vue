<template>
    <div class="wma-chart">
      <h3>{{ symbol }} WMA Chart</h3>
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
      }),
    },
    watch: {
      symbol: "fetchChartData",
    },
    methods: {
      ...mapActions("stockApp", ["fetchSMAChartData"]),
      async fetchChartData() {
        this.chartData = null;
        await this.fetchSMAChartData(this.symbol);
        if (!this.error) {
          this.chartData = this.$store.state.stockApp.chartData;
          await nextTick(); // 確保 DOM 更新完成
          this.renderChart();
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
  
        const layout = {
          title: `${this.symbol} WMA Chart(權重)`,
          xaxis: { title: "Date" },
          yaxis: { title: "Price" },
          showlegend: true,
          hovermode: "x unified"
        };
  
        Plotly.newPlot(this.$refs.chartContainer, [traceCandlestick, traceWMA5, traceWMA20], layout);
      },
    },
    mounted() {
      this.fetchChartData();
    },
  };
  </script>
  
  <style scoped>
  .wma-chart {
    margin-top: 20px;
  }
  
  .loading {
    color: #007bff;
  }
  
  .error {
    color: #ff0000;
  }
  </style>