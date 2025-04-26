<template>
  <div class="stock-chart">
    <div class="stock-chart-title">{{ symbol }} Stock Price Chart</div>
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  props: {
    symbol: {
      type: String,
      required: true
    },
    chartData: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      error: null
    };
  },
  watch: {
    chartData: 'renderChart'
  },
  methods: {
    renderChart() {
      const { dates, close_prices } = this.chartData;
      const trace = {
        x: dates,
        y: close_prices,
        type: 'scatter',
        mode: 'lines+markers',
        name: this.symbol,
        line: { color: '#2894FF' }
      };
      const layout = {
        xaxis: { title: 'Date', color: '#BEBEBE', gridcolor: '#7B7B7B'},
        yaxis: { title: 'Close Price', color: '#BEBEBE', gridcolor: '#7B7B7B'},
        paper_bgcolor: '#4F4F4F',
        plot_bgcolor: '#4F4F4F',
      };
      Plotly.newPlot(this.$refs.chartContainer, [trace], layout);
    }
  },
  mounted() {
    this.renderChart();
  }
};
</script>

<style scoped>
.stock-chart {
  margin-top: 20px;
  background-color: #4F4F4F;
}

.stock-chart-title{
  font-size: 25px;
  line-height: 25px;
  padding: 10px;
  padding-bottom: 20px;
  border-bottom: 2px solid #7B7B7B
}

.loading {
  color: #007bff;
}

.error {
  color: #ff0000;
}
</style>