<template>
  <div class="birth-rate-chart">
    <loading-spinner v-if="loading" />
    <error-message
      v-else-if="error"
      :message="error"
      retryable
      @retry="fetchData"
    />
    <div v-else>
      <div class="chart-container" ref="chartContainer"></div>
      <div class="chart-summary">
        <div class="summary-item">
          <h4>整體變化趨勢</h4>
          <p>{{ getTrend }}</p>
        </div>
        <div class="summary-item">
          <h4>最大降幅</h4>
          <p>{{ getMaxDecline }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { mapState, mapActions } from "vuex";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";

  export default {
    name: "BirthRateChart",
    components: {
      LoadingSpinner,
      ErrorMessage,
    },
    data() {
      return {
        chart: null,
      };
    },
    computed: {
      ...mapState("birthRate", {
        loading: (state) => state.loading,
        error: (state) => state.error,
        chartData: (state) => state.yearlyData,
      }),
      getTrend() {
        if (!this.chartData.length) return "數據不足";
        const firstValue = this.chartData[0].value;
        const lastValue = this.chartData[this.chartData.length - 1].value;
        return lastValue > firstValue ? "上升" : "下降";
      },
      getMaxDecline() {
        if (!this.chartData.length) return 0;
        let maxDecline = 0;
        for (let i = 1; i < this.chartData.length; i++) {
          const decline =
            ((this.chartData[i - 1].value - this.chartData[i].value) /
              this.chartData[i - 1].value) *
            100;
          maxDecline = Math.max(maxDecline, decline);
        }
        return maxDecline.toFixed(2);
      },
    },
    mounted() {
      this.fetchData();
    },
    methods: {
      ...mapActions("birthRate", ["fetchData"]),
      initChart() {
        const data = [
          {
            x: this.chartData.map((d) => d.year),
            y: this.chartData.map((d) => d.value),
            type: "scatter",
            mode: "lines+markers",
            name: "出生率",
            line: { color: "#2196f3" },
          },
        ];

        const layout = {
          title: "出生率變化趨勢",
          xaxis: {
            title: "年份",
          },
          yaxis: {
            title: "出生率",
            rangemode: "tozero",
          },
          margin: {
            t: 40,
            b: 40,
            l: 40,
            r: 40,
          },
        };

        // 清空之前的圖表
        this.$refs.chartContainer.innerHTML = "";

        // 使用 Plotly.js 來創建圖表
        Plotly.newPlot(this.$refs.chartContainer, data, layout);
      },
    },
    watch: {
      chartData: {
        handler(newData) {
          if (newData.length) {
            this.initChart();
          }
        },
        deep: true,
      },
    },
  };
</script>

<style scoped>
  .birth-rate-chart {
    padding: 20px;
  }

  .chart-container {
    height: 400px;
    margin-bottom: 20px;
  }

  .chart-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    padding: 20px;
    background-color: #f5f5f5;
    border-radius: 8px;
  }

  .summary-item {
    text-align: center;
  }

  .summary-item h4 {
    margin-bottom: 8px;
    color: #333;
  }

  .summary-item p {
    font-size: 1.2em;
    font-weight: bold;
    color: #2196f3;
  }
</style>
