<template>
  <div class="stock-chart">
    <h3>{{ symbol }} Chart</h3>
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
        line: { color: '#17BECF' }
      };
      const layout = {
        title: `${this.symbol} Stock Price`,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Close Price' }
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
}

h3{
  font-size: 25px;
}

.loading {
  color: #007bff;
}

.error {
  color: #ff0000;
}
</style>