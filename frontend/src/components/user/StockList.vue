<!-- StockList.vue -->
<template>
  <div class="stocks-list">
    <div v-for="stock in stocks" :key="stock" class="stock-item">
      <div class="stock-info">
        <span class="stock-code" @click.stop="$emit('navigate', stock)">
          {{ stock }}
        </span>
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
      <button
        class="remove-stock-btn"
        @click.stop="$emit('remove-stock', stock)"
      >
        <span class="material-icons">close</span>
      </button>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      stocks: Array,
      chartData: Object,
    },
  };
</script>

<style scoped>
  .stocks-list {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    max-height: 240px;
    overflow-y: auto;
    padding-right: 8px;
  }

  .stock-item {
    flex: 0 0 calc(25% - 9px);
    display: flex;
    align-items: center;
    background: white;
    padding: 8px 15px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    min-height: 48px;
    position: relative;
  }

  .stock-info {
    display: flex;
    align-items: center;
    gap: 15px;
    width: calc(100% - 30px);
  }

  .stock-code {
    font-weight: 500;
    color: #2c3e50;
    cursor: pointer;
  }

  .stock-change {
    font-size: 0.9em;
    min-width: 60px;
    text-align: right;
  }

  .remove-stock-btn {
    position: absolute;
    right: 8px;
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 4px;
  }

  .positive {
    color: #4caf50;
  }
  .negative {
    color: #f44336;
  }
</style>
