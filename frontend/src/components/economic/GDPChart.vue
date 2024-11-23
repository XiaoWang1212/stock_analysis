<template>
    <div class="gdp-chart">
      <loading-spinner v-if="loading" />
      <error-message
        v-else-if="error"
        :message="error"
        retryable
        @retry="fetchData"
      />
      <div v-else class="chart-wrapper">
        <div class="chart-container" ref="chartContainer"></div>
        <div class="recovery-progress">
          <div class="progress-bar" :style="{ width: `${recoveryRate}%` }"></div>
          <span>{{ recoveryRate }}%</span>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import Plotly from 'plotly.js-dist';
  import { mapState, mapActions } from 'vuex';
  import LoadingSpinner from '../common/LoadingSpinner.vue';
  import ErrorMessage from '../common/ErrorMessage.vue';
  
  export default {
    name: 'GDPChart',
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
      ...mapState('economic', {
        loading: (state) => state.loading,
        error: (state) => state.error,
        chartData: (state) => state.gdpData,
      }),
      recoveryRate() {
        if (!this.chartData.length) return 0;
        const firstValue = this.chartData[0].value;
        const lastValue = this.chartData[this.chartData.length - 1].value;
        return ((lastValue - firstValue) / firstValue * 100).toFixed(2);
      }
    },
    mounted() {
      this.fetchData();
    },
    methods: {
      ...mapActions('economic', ['fetchData']),
      initChart() {
        const data = [
          {
            x: this.chartData.map((d) => d.year),
            y: this.chartData.map((d) => d.value),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'GDP',
            line: { color: '#42A5F5' },
          },
        ];
  
        const layout = {
          title: 'GDP 變化趨勢',
          xaxis: {
            title: '年份',
          },
          yaxis: {
            title: 'GDP',
            rangemode: 'tozero',
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
  .gdp-chart {
    padding: 20px;
  }
  
  .chart-wrapper {
    height: 400px;
    margin-bottom: 20px;
  }
  
  .chart-container {
    height: 100%;
  }
  
  .recovery-progress {
    display: flex;
    align-items: center;
    margin-top: 20px;
  }
  
  .progress-bar {
    height: 20px;
    background-color: #42A5F5;
    border-radius: 4px;
    flex-grow: 1;
    margin-right: 10px;
  }
  
  .recovery-progress span {
    font-size: 1.2em;
    font-weight: bold;
    color: #333;
  }
  </style>