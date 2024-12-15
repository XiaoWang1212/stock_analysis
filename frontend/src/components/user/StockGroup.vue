<!-- StockGroup.vue -->
<template>
    <div class="group-card" :class="{ expanded: isExpanded }" @click="$emit('toggle')">
      <div class="expand-handle">
        <span class="material-icons">
          {{ isExpanded ? "expand_less" : "expand_more" }}
        </span>
      </div>
      <div class="group-content">
        <div class="group-header">
          <input
            v-model="localGroupName"
            @change="$emit('update-name', groupName)"
            class="group-name-input"
            :placeholder="`群組 ${index + 1}`"
            @click.stop
          />
          <button @click.stop="$emit('add-stock')" class="add-stock-btn">
            <span class="material-icons">add</span>
            添加股票
          </button>
        </div>
        
        <stock-list
          v-if="!isExpanded"
          :stocks="stocks"
          :chartData="chartData"
          @remove-stock="$emit('remove-stock', $event)"
          @navigate="$emit('navigate', $event)"
        />
        
        <stock-chart-grid
          v-else
          :stocks="stocks"
          :chartData="chartData"
          @navigate="$emit('navigate', $event)"
        />
      </div>
    </div>
  </template>
  
  <script>
  import StockList from './StockList.vue'
  import StockChartGrid from './StockChartGrid.vue'
  
  export default {
    components: {
      StockList,
      StockChartGrid
    },
    props: {
      index: Number,
      stocks: Array,
      chartData: Object,
      isExpanded: Boolean,
      groupName: String
    },
    emits: ['toggle', 'update-name', 'add-stock', 'remove-stock', 'navigate'],
    data() {
      return {
        localGroupName: this.groupName
      };
    },
    watch: {
      groupName(newVal) {
        this.localGroupName = newVal;
      },
      localGroupName(newVal) {
        this.$emit('update-name', newVal);
      }
    }
  }
  </script>

<style scoped>
.group-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
  min-height: 200px;
  cursor: pointer;
  position: relative;
  transition: transform 0.3s ease-out;
}

.group-card.expanded {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90vw;
  height: 90vh;
  background: white;
  z-index: 999;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.group-name-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9em;
}

.add-stock-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 15px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.expand-handle {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
}
</style>