<!-- StockChartGrid.vue -->
<template>
  <div class="charts-grid">
    <div
      v-for="stock in stocks"
      :key="stock"
      class="stock-chart-item"
      @click.stop="$emit('navigate', stock)"
    >
      <div class="stock-info">
        <span class="stock-symbol">{{ stock }}</span>
        <span
          class="stock-change"
          :class="{
            positive: chartData[stock]?.change > 0,
            negative: chartData[stock]?.change < 0,
          }"
        >
          {{ chartData[stock]?.change }}%
        </span>
      </div>
      <mini-stock-chart v-if="chartData[stock]" :chartData="chartData[stock]" />
    </div>
  </div>
</template>

<script>
  import MiniStockChart from "../stock/MiniStockChart.vue";

  export default {
    components: {
      MiniStockChart,
    },
    props: {
      stocks: Array,
      chartData: Object,
    },
  };
</script>

<style scoped>
  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 15px;
    padding: 15px;
  }

  .stock-chart-item {
    background: white;
    border-radius: 8px;
    padding: 12px 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    display: flex;
    flex-direction: column;
    height: 220px;
    cursor: pointer;
  }

  .stock-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    padding-bottom: 0;
    height: auto;
    min-height: 24px;
  }

  .stock-symbol {
    font-size: 1em;
    font-weight: 500;
    color: #2c3e50;
  }

  .stock-change {
    font-size: 0.95em;
    min-width: 70px;
    text-align: right;
  }

  .positive {
    color: #4caf50;
  }
  .negative {
    color: #f44336;
  }
</style>
