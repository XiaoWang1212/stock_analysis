<template>
  <div class="sma-bias-chart">
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
        "fetchBIASChartData",
        "generateTwStockNameMap",
        "setCurrentMarket",
      ]),

      async fetchChartData() {
        this.chartData = null;

        if (
          this.market === "TW" &&
          (!this.twStockNameMap ||
            Object.keys(this.twStockNameMap).length === 0)
        ) {
          await this.generateTwStockNameMap();
        }

        await this.fetchBIASChartData(this.symbol, this.market);

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

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const biasDiffIndices = [];
        const biasDiffValues = [];

        // 僅收集有效的 bias_diff 數據點
        for (let i = 0; i < bias_diff.length; i++) {
          if (bias_diff[i] !== null) {
            biasDiffIndices.push(indices[i]);
            biasDiffValues.push(bias_diff[i]);
          }
        }

        const traceCandlestick = {
          x: indices,
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
          text: dates,
        };

        const traceSMA5 = {
          x: indices,
          y: sma_5,
          type: "scatter",
          mode: "lines",
          name: "SMA 5",
          xaxis: "x",
          yaxis: "y",
          line: { color: "black" },
        };

        const traceSMA20 = {
          x: indices,
          y: sma_20,
          type: "scatter",
          mode: "lines",
          name: "SMA 20",
          xaxis: "x",
          yaxis: "y",
          line: { color: "blue" },
        };

        const traceSMA60 = {
          x: indices,
          y: sma_60,
          type: "scatter",
          mode: "lines",
          name: "SMA 60",
          xaxis: "x",
          yaxis: "y",
          line: { color: "aqua" },
        };

        const traceBIAS10 = {
          x: indices,
          y: bias_10,
          type: "scatter",
          mode: "lines",
          name: "BIAS 10",
          xaxis: "x2",
          yaxis: "y2",
          line: { color: "black" },
          hoverinfo: "skip",
        };

        const traceBIAS20 = {
          x: indices,
          y: bias_20,
          type: "scatter",
          mode: "lines",
          name: "BIAS 20",
          xaxis: "x2",
          yaxis: "y2",
          line: { color: "blue" },
          hoverinfo: "skip",
        };

        const traceBIASDiff = {
          x: biasDiffIndices,
          y: biasDiffValues,
          type: "bar",
          name: "BIAS Diff",
          xaxis: "x2",
          yaxis: "y2",
          marker: {
            color: biasDiffValues.map((value) =>
              value >= 0 ? "red" : "green"
            ),
          },
          text: biasDiffIndices.map((i) => dates[i]), // 為每個點添加日期文本
          customdata: biasDiffIndices.map((i) => dates[i]),
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>BIAS Diff:</b> %{y:.2f}%<br>" +
            "<extra></extra>",
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` (${this.displayName})`;
        }
        chartTitle += ` SMA and BIAS Chart`;

        const layout = {
          title: chartTitle,
          grid: { rows: 2, columns: 1, pattern: "independent" },
          xaxis: {
            title: "Date",
            rangeslider: { visible: false },
            tickmode: "array",
            tickvals: indices.filter(
              (_, i) =>
                i === 0 ||
                i === indices.length - 1 ||
                i % Math.ceil(indices.length / 8) === 0
            ),
            // 這些位置上顯示的文本為對應日期
            ticktext: indices
              .filter(
                (_, i) =>
                  i === 0 ||
                  i === indices.length - 1 ||
                  i % Math.ceil(indices.length / 8) === 0
              )
              .map((i) => dates[i]),
            tickangle: -45,
          },
          yaxis: { title: "Price" },
          xaxis2: {
            title: "Date",
            tickmode: "array",
            tickvals: indices.filter(
              (_, i) =>
                i === 0 ||
                i === indices.length - 1 ||
                i % Math.ceil(indices.length / 8) === 0
            ),
            ticktext: indices
              .filter(
                (_, i) =>
                  i === 0 ||
                  i === indices.length - 1 ||
                  i % Math.ceil(indices.length / 8) === 0
              )
              .map((i) => dates[i]),
            tickangle: -45,
          },
          yaxis2: { title: "BIAS %" },
          showlegend: true,
          hovermode: "x unified",
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
