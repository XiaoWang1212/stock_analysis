<template>
  <div class="ema-chart">
    <h3>{{ symbol }} EMA Chart</h3>
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
          ema_5,
          ema_20,
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

        const traceEMA5 = {
          x: dates,
          y: ema_5,
          type: "scatter",
          mode: "lines",
          name: "EMA 5",
          line: { color: "black" },
        };

        const traceEMA20 = {
          x: dates,
          y: ema_20,
          type: "scatter",
          mode: "lines",
          name: "EMA 20",
          line: { color: "blue" },
        };

        const layout = {
          title: `${this.symbol} EMA Chart(指數)`,
          xaxis: { title: "Date" },
          yaxis: { title: "Price" },
          showlegend: true,
          hovermode: "x unified", // 提供更友好的 hover 效果
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceCandlestick, traceEMA5, traceEMA20],
          layout
        );
      },
    },
    mounted() {
      this.fetchChartData();
    },
  };
</script>

<style scoped>
  .ema-chart {
    margin-top: 20px;
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }
</style>
