<template>
  <div class="sma-chart">
    <h3>{{ symbol }} SMA Chart</h3>
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
          sma_5,
          sma_20,
          sma_60,
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

        const traceSMA5 = {
          x: dates,
          y: sma_5,
          type: "scatter",
          mode: "lines",
          name: "SMA 5",
          line: { color: "black" },
        };

        const traceSMA20 = {
          x: dates,
          y: sma_20,
          type: "scatter",
          mode: "lines",
          name: "SMA 20",
          line: { color: "blue" },
        };

        const traceSMA60 = {
          x: dates,
          y: sma_60,
          type: "scatter",
          mode: "lines",
          name: "SMA 60",
          line: { color: "aqua" },
        };

        const layout = {
          title: `${this.symbol} SMA Chart(簡單)`,
          xaxis: { title: "Date" },
          yaxis: { title: "Price" },
          showlegend: true,
          hovermode: "x unified", // 提供更友好的 hover 效果
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceCandlestick, traceSMA5, traceSMA20, traceSMA60],
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
  .sma-chart {
    margin-top: 20px;
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }
</style>
