<template>
  <div class="sma-bias-chart">
    <h3>{{ symbol }} SMA and BIAS Analysis</h3>
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
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        error: (state) => state.error,
        storeChartData: (state) => state.chartData,
      }),
    },
    watch: {
      symbol() {
        this.fetchChartData();
      },
      market() {
        this.fetchChartData();
      },
    },
    methods: {
      ...mapActions("stockApp", ["fetchBIASChartData", "setCurrentMarket"]),
      async fetchChartData() {
        this.chartData = null;

        this.setCurrentMarket(this.market);

        await this.fetchBIASChartData(this.symbol);

        this.chartData = this.$store.state.stockApp.chartData;

        if (!this.error) {
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
          bias_10,
          bias_20,
          bias_diff,
        } = this.chartData;
        // 僅包括有數據的日期
        const validDates = dates.filter(
          (_, index) => bias_diff[index] !== null
        );
        const validBiasDiff = bias_diff.filter((value) => value !== null);
        const traceCandlestick = {
          x: dates,
          close: close_prices,
          high: high_prices,
          low: low_prices,
          open: open_prices,
          type: "candlestick",
          name: "Candlestick",
          xaxis: "x",
          yaxis: "y",
          increasing: { line: { color: "#FF0000" }, fillcolor: "#FFCCCC" },
          decreasing: { line: { color: "#008000" }, fillcolor: "#CCFFCC" },
        };

        const traceSMA5 = {
          x: dates,
          y: sma_5,
          type: "scatter",
          mode: "lines",
          name: "SMA 5",
          xaxis: "x",
          yaxis: "y",
          line: { color: "black" },
        };

        const traceSMA20 = {
          x: dates,
          y: sma_20,
          type: "scatter",
          mode: "lines",
          name: "SMA 20",
          xaxis: "x",
          yaxis: "y",
          line: { color: "blue" },
        };

        const traceSMA60 = {
          x: dates,
          y: sma_60,
          type: "scatter",
          mode: "lines",
          name: "SMA 60",
          xaxis: "x",
          yaxis: "y",
          line: { color: "aqua" },
        };

        const traceBIAS10 = {
          x: dates,
          y: bias_10,
          type: "scatter",
          mode: "lines",
          name: "BIAS 10",
          xaxis: "x2",
          yaxis: "y2",
          line: { color: "black" },
        };

        const traceBIAS20 = {
          x: dates,
          y: bias_20,
          type: "scatter",
          mode: "lines",
          name: "BIAS 20",
          xaxis: "x2",
          yaxis: "y2",
          line: { color: "blue" },
        };

        const traceBIASDiff = {
          x: validDates,
          y: validBiasDiff,
          type: "bar",
          name: "BIAS Diff",
          xaxis: "x2",
          yaxis: "y2",
          marker: {
            color: validBiasDiff.map((value) => (value >= 0 ? "red" : "green")),
          },
        };

        const layout = {
          title: `${this.symbol} SMA and BIAS Chart`,
          grid: { rows: 2, columns: 1, pattern: "independent" },
          xaxis: { title: "Date", rangeslider: { visible: false } },
          yaxis: { title: "Price" },
          xaxis2: { title: "Date" },
          yaxis2: { title: "BIAS" },
          showlegend: true,
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [
            traceCandlestick,
            traceSMA5,
            traceSMA20,
            traceSMA60,
            traceBIAS10,
            traceBIAS20,
            traceBIASDiff,
          ],
          layout
        );
      },
    },
    mounted() {
      this.fetchChartData();
    },
    beforeUnmount() {
      if (this.$refs.chartContainer) {
        Plotly.purge(this.$refs.chartContainer);
      }
    },
  };
</script>

<style scoped>
  .sma-bias-chart {
    margin-top: 20px;
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }
</style>
