<template>
  <div class="stoch-chart">
    <h3>{{ symbol }} STOCH Chart</h3>
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是隨機指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>隨機指標(STOCH)</p>
      <p>
        又稱為KD指標，顧名思義是由K值與D值組合而成。K值為快速平均值，對股市近期變化較為敏感；D值為慢速平均值，對股市近期變化較為遲緩，因此投資人多利用KD指標的相對位置作為進出場時機的判斷輔助
      </p>
      <p>
        根據繪製出的圖表，可觀察K值（橘線）與D值（綠線）的交叉時機，判斷進出場時機，除此之外，也可透過KD值觀察市場上超買或超賣的情形，捕捉價格修正的情形
      </p>
      <img src="@/assets/photos/STOCH.png" alt="STOCH Photo" />
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
        const { dates, slowk, slowd } = this.chartData;

        const traceK = {
          x: dates,
          y: slowk,
          type: "scatter",
          mode: "lines",
          name: "K值",
          line: { color: "orange" },
        };

        const traceD = {
          x: dates,
          y: slowd,
          type: "scatter",
          mode: "lines",
          name: "D值",
          line: { color: "green" },
        };

        const layout = {
          title: `${this.symbol} STOCH Chart`,
          xaxis: { title: "Date" },
          showlegend: true,
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceK, traceD],
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
  .stoch-chart {
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
