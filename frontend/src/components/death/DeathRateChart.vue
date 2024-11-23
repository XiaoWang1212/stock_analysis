<template>
    <div class="death-rate-chart">
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
            <h4>最大增幅</h4>
            <p>{{ getMaxIncrease }}%</p>
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
    name: "DeathRateChart",
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
      ...mapState("deathRate", {
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
      getMaxIncrease() {
        if (!this.chartData.length) return 0;
        let maxIncrease = 0;
        for (let i = 1; i < this.chartData.length; i++) {
          const increase =
            ((this.chartData[i].value - this.chartData[i - 1].value) /
              this.chartData[i - 1].value) *
            100;
          maxIncrease = Math.max(maxIncrease, increase);
        }
        return maxIncrease.toFixed(2);
      },
    },
    mounted() {
      this.fetchData();
    },
    methods: {
      ...mapActions("deathRate", ["fetchData"]),
      initChart() {
        const data = [
          {
            x: this.chartData.map((d) => d.year),
            y: this.chartData.map((d) => d.value),
            type: "scatter",
            mode: "lines+markers",
            name: "死亡率",
            line: { color: "#e53935" },
          },
        ];
  
        const layout = {
          title: "死亡率變化趨勢",
          xaxis: {
            title: "年份",
          },
          yaxis: {
            title: "死亡率",
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
  .death-rate-chart {
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
    color: #e53935;
  }
  </style>