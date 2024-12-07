<!-- MiniStockChart.vue 完整修改 -->
<template>
  <div class="mini-chart" ref="chartContainer"></div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  name: 'MiniStockChart',
  props: {
    chartData: {
      type: Object,
      required: true
    }
  },
  methods: {
    renderChart() {
      const trace = {
        x: this.chartData.dates,
        y: this.chartData.close_prices,
        type: 'scatter',
        mode: 'lines',
        line: {
          color: '#17BECF',
          width: 1.5
        },
        hoverinfo: 'none'
      };

      const layout = {
        showlegend: false,
        margin: { t: 0, r: 0, l: 0, b: 0 },
        xaxis: {
          showgrid: false,
          zeroline: false,
          showticklabels: false,
          fixedrange: true
        },
        yaxis: {
          showgrid: false,
          zeroline: false,
          showticklabels: false,
          fixedrange: true
        },
        width: 150,
        height: 50,
        plot_bgcolor: '#ffffff',  // 白色背景
        paper_bgcolor: '#ffffff'  // 白色背景
      };

      const config = {
        displayModeBar: false,
        responsive: true
      };

      Plotly.newPlot(this.$refs.chartContainer, [trace], layout, config);
    }
  },
  watch: {
    chartData: {
      handler() {
        this.$nextTick(() => {
          this.renderChart();
        });
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.renderChart();
    });
  }
};
</script>

<style scoped>
.mini-chart {
  display: inline-block;
  width: 150px;
  height: 50px;
  background-color: #ffffff;
  border-radius: 4px;
  overflow: hidden;
}

/* 修改 StockHeatmap.vue 中的懸浮資訊面板樣式 */
.hover-info {
  position: fixed;
  z-index: 1000;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  min-width: 300px;
  max-height: 80vh;
  overflow-y: auto;
}

.stock-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stock-item:last-child {
  border-bottom: none;
}
</style>