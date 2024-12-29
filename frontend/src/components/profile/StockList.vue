<template>
  <div class="stocks-container" :class="{ expanded: isExpanded }">
    <div v-if="!isExpanded && stocks?.length" class="stocks-list">
      <div
        v-for="stock in stocks"
        :key="stock"
        class="stock-item"
        @click.stop="$emit('navigate', stock)"
      >
        <!-- 基本資訊 -->
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
        <button
          class="remove-stock-btn"
          @click.stop="$emit('remove-stock', stock)"
        >
          <span class="material-icons">close</span>
        </button>
      </div>
    </div>

    <!-- 展開後的網格 -->
    <div v-if="isExpanded && stocks?.length" class="charts-grid">
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
          <button
            class="remove-stock-btn"
            @click.stop="$emit('remove-stock', stock)"
          >
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="mini-chart-container">
          <mini-stock-chart :chartData="chartData[stock]" />
        </div>
      </div>
    </div>

    <div v-if="!stocks?.length" class="empty-stocks">尚未添加任何股票</div>
  </div>
</template>

<script>
  import MiniStockChart from "@/components/stock/MiniStockChart.vue";

  export default {
    name: "StockList",
    components: {
      MiniStockChart,
    },
    props: {
      stocks: {
        type: Array,
        default: () => [],
      },
      chartData: {
        type: Object,
        default: () => ({}),
      },
      isExpanded: {
        type: Boolean,
        default: false,
      },
    },
    emits: ["navigate", "remove-stock"],
  };
</script>

<style scoped>
  .stocks-container {
    width: 100%;
    transition: all 0.3s ease;
    position: relative;
  }

  .stocks-list {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    max-height: 240px;
    overflow-y: auto;
    padding-right: 8px;
    scrollbar-width: thin;
    scrollbar-color: #c1c1c1 #f1f1f1;
  }

  .expanded .stocks-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 30px;
    transition: none;
  }

  .stocks-list::-webkit-scrollbar {
    width: 6px;
  }

  .stocks-list::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  .stocks-list::-webkit-scrollbar-thumb {
    background: #888;
  }

  .stock-item {
    flex: 0 0 calc(25% - 9px);
    display: flex;
    justify-content: space-between;
    gap: 10px;
    background: white;
    padding: 8px 15px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    min-width: 140px;
    min-height: 48px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
  }

  .expanded .stock-item {
    padding: 15px 20px;
    font-size: 1.1em;
    transform: none;
    transition: none;
  }

  .stock-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .stock-item:hover .stock-symbol {
    color: #4a90e2;
  }

  .stock-info {
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    flex: 1;
    height: 100%;
    width: calc(100% - 20px);
  }

  .expanded .stock-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 15px;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    width: 100%;
  }

  .stock-symbol,
  .stock-change {
    display: flex;
    align-items: center;
    font-size: 0.95em;
  }

  .expanded .stock-symbol,
  .expanded .stock-change {
    font-size: 1.1em;
    font-weight: 500;
  }

  .expanded .stock-change {
    min-width: 80px;
    text-align: right;
  }

  .stock-symbol {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
    color: #2c3e50;
    cursor: pointer;
    padding: 2px 0;
  }

  .stock-change {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
    font-size: 0.9em;
    min-width: 50px;
    max-width: 50px;
    text-align: right;
    margin-right: 20px;
  }

  .positive {
    color: #4caf50;
    background: rgba(76, 175, 80, 0.1);
  }

  .negative {
    color: #f44336;
    background: rgba(244, 67, 54, 0.1);
  }

  .remove-stock-btn {
    position: absolute;
    background: none;
    right: 8px;
    top: 50%;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 2px;
    display: flex;
    align-items: center;
    transform: translateY(-50%);
  }

  .remove-stock-btn:hover {
    color: #ff4d4d;
  }

  .empty-stocks {
    text-align: center;
    padding: 20px;
    color: #666;
    border: 2px dashed #e0e0e0;
    border-radius: 8px;
    margin-top: 15px;
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
    position: relative;
  }

  .stock-chart-item .stock-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid #eee;
    width: calc(100% - 30px);
  }

  .stock-chart-item .stock-change {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
    min-width: 60px;
    text-align: right;
    margin-right: 5px;
    justify-content: center;
  }

  .stock-chart-item .remove-stock-btn {
    position: absolute;
    top: 10px;
    right: 10px;
  }

  .stock-chart-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  }

  .stock-chart-item .mini-chart-container {
    flex: 1;
    position: relative;
    min-height: 200px;
    width: 100%;
  }

  .expanded .mini-chart-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
  }

  .mini-chart {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    max-height: 160px;
    width: 100%;
    margin-bottom: 10px;
  }

  .remove-stock-btn {
    pointer-events: auto;
  }
</style>
