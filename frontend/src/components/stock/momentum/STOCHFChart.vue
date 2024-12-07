<template>
  <div class="stochf-chart">
    <h3>{{ symbol }} STOCHF Chart</h3>
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是隨機快速指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>隨機快速指標(STOCHF)</p>
      <p>
        隨機快速指標，從隨機指標延伸而來，與隨機指標差別在於，隨機快速指標以RSV值計算公式取代隨機指標的K值計算方式，減少一次的平滑運算，因此對於短期股市趨勢反應較為敏感
      </p>
      <p>
        STOCHF常用的觀察方式為，下降的K線穿越超買區域的D線時，即產生賣出信號；上升的K線穿越超賣區域的D線時，即產生買入信號
      </p>
      <img src="@/assets/photos/STOCHF.png" alt="STOCHF Photo" />
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
        const { dates, stochf_fastk, stochf_fastd } = this.chartData;

        const traceK = {
          x: dates,
          y: stochf_fastk,
          type: "scatter",
          mode: "lines",
          name: "K值",
          line: { color: "purple" },
        };

        const traceD = {
          x: dates,
          y: stochf_fastd,
          type: "scatter",
          mode: "lines",
          name: "D值",
          line: { color: "gray" },
        };

        const layout = {
          title: `${this.symbol} STOCHF Chart`,
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
  .stochf-chart {
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
