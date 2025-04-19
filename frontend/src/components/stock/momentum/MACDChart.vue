<template>
  <div class="macd-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是平滑異同移動平均線指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>平滑異同移動平均線指標(MACD)</p>
      <p>
        MACD指標是透過DIF線與MACD線的交叉，來判斷買入與賣出的訊號。除此之外，若股價創新低，但MACD線卻出現上升的情形，常被認為是買入訊號，即為多頭背離，相反，若股價創新高，但MACD線卻出現下降的情形，常被認為是賣出訊號，即為空頭背離
      </p>
      <img src="@/assets/photos/MACD.png" alt="MACD Photo" />
    </div>
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
        showInfo: false,
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
      ...mapActions("stockApp", ["fetchSMAChartData", "generateTwStockNameMap"]),
      async fetchChartData() {
        this.chartData = null;

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
          await nextTick(); // 確保 DOM 更新完成
          this.renderChart();
        }
      },
      async renderChart() {
        await nextTick(); // 確保 DOM 更新完成
        const { dates, macd, macd_signal } = this.chartData;

        const traceDIF = {
          x: dates,
          y: macd,
          type: "scatter",
          mode: "lines",
          name: "DIF",
          line: { color: "black" },
        };

        const traceMACD = {
          x: dates,
          y: macd_signal,
          type: "scatter",
          mode: "lines",
          name: "MACD",
          line: { color: "blue" },
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` (${this.displayName})`;
        }
        chartTitle += ` MACD Chart`;
        
        const layout = {
          title: chartTitle,
          xaxis: { title: "Date" },
          showlegend: true,
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceDIF, traceMACD],
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
  .macd-chart {
    margin-top: 20px;
    position: relative;
  }

  .chart-container {
    position: relative;
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }

  .info-container {
    cursor: pointer;
    display: flex;
    align-items: center;
    position: absolute;
    top: 10px;
    right: 160px;
  }

  .info-icon {
    font-size: 24px;
    margin-right: 5px;
  }

  .info-text {
    font-size: 14px;
    color: #007bff;
  }

  .info-box {
    background-color: #f9f9f9;
    border: 1px solid #ccc;
    padding: 10px;
    position: absolute;
    top: 40px;
    right: 10px;
    width: 300px;
    z-index: 1000;
  }

  .info-box img {
    max-width: 100%;
    height: auto;
  }
</style>
