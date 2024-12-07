<template>
  <div class="rsi-chart">
    <h3>{{ symbol }} RSI Chart</h3>
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是相對強弱指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>相對強弱指標(RSI)</p>
      <p>
        由股價的平均上漲、下跌幅度計算而得，代表股價的上漲力道強弱，數值介於0~100之間，數值越大代表上漲力道越強。
      </p>
      <img src="@/assets/photos/RSI.png" alt="RSI Photo" />
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
        const { dates, rsi_6, rsi_24 } = this.chartData;

        const traceRSI6 = {
          x: dates,
          y: rsi_6,
          type: "scatter",
          mode: "lines",
          name: "RSI 6",
          line: { color: "black" },
        };

        const traceRSI24 = {
          x: dates,
          y: rsi_24,
          type: "scatter",
          mode: "lines",
          name: "RSI 24",
          line: { color: "blue" },
        };

        const layout = {
          title: `${this.symbol} RSI Chart`,
          xaxis: { title: "Date" },
          yaxis: { title: "RSI" },
          showlegend: true,
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceRSI6, traceRSI24],
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
  .rsi-chart {
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
