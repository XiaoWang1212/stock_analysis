<template>
    <div v-if="show" class="dialog-overlay" @click="$emit('close')">
      <div class="dialog-content" @click.stop>
        <h3>添加股票</h3>
        
        <div class="search-container">
          <input
            v-model="searchText"
            class="search-input"
            placeholder="輸入股票代號..."
            @input="handleInput"
            ref="searchInput"
          />
          
          <div v-if="showSuggestions && filteredStocks.length" class="suggestions">
            <div
              v-for="stock in filteredStocks"
              :key="stock"
              class="suggestion-item"
              @click="selectStock(stock)"
            >
              {{ stock }}
            </div>
          </div>
        </div>
  
        <div class="dialog-buttons">
          <button class="cancel-btn" @click="$emit('close')">取消</button>
          <button 
            class="confirm-btn" 
            @click="handleConfirm"
            :disabled="!searchText"
          >
            確認
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      show: Boolean,
      stockList: {
        type: Array,
        default: () => []
      }
    },
    data() {
      return {
        searchText: '',
        showSuggestions: false,
        filteredStocks: []
      }
    },
    watch: {
      show(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            this.$refs.searchInput?.focus();
          });
        } else {
          this.searchText = '';
          this.showSuggestions = false;
        }
      }
    },
    methods: {
      handleInput() {
        if (this.searchText) {
          const query = this.searchText.toUpperCase();
          this.filteredStocks = this.stockList
            .filter(stock => stock.startsWith(query))
            .slice(0, 8);
          this.showSuggestions = this.filteredStocks.length > 0;
        } else {
          this.showSuggestions = false;
          this.filteredStocks = [];
        }
      },
      selectStock(stock) {
        this.searchText = stock;
        this.showSuggestions = false;
      },
      handleConfirm() {
        if (this.searchText) {
          this.$emit('confirm', this.searchText.toUpperCase());
          this.$emit('close');
        }
      }
    }
  }
  </script>
  
  <style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  padding: 30px;  /* 增加內部間距 */
  border-radius: 16px;  /* 增加圓角 */
  width: 90%;
  max-width: 450px;  /* 增加最大寬度 */
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

h3 {
  font-size: 1.4em;  /* 加大標題 */
  margin: 0 0 25px;  /* 增加下方間距 */
  color: #2c3e50;
}

.search-container {
  position: relative;
  margin-bottom: 25px; 
}

.search-input {
  width: 80%;
  padding: 14px 16px; 
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.suggestions {
  position: absolute;
  top: calc(100% + 5px);  /* 調整建議列表位置 */
  left: 0;
  width: 90%;
  max-height: 250px;  /* 增加最大高度 */
  overflow-y: auto;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-item:hover {
  background-color: #f5f7fa;
}

.dialog-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 15px;  /* 增加按鈕間距 */
  margin-top: 30px;  /* 增加上方間距 */
}

.dialog-buttons button {
  min-width: 100px;  /* 設定最小寬度 */
  padding: 10px 24px;  /* 調整按鈕內距 */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;  /* 加粗字體 */
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: #f3f4f6;
  color: #4b5563;
}

.cancel-btn:hover {
  background-color: #e5e7eb;
}

.confirm-btn {
  background-color: #4a90e2;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #357abd;
  transform: translateY(-1px);
}

.confirm-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}
</style>