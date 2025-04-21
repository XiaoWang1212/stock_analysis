<template>
  <div class="tw-stock-categories">
    <h1>台股產業分類</h1>

    <loading-spinner v-if="loading" />
    <error-message v-else-if="error" :message="error" @retry="fetchStockList" />

    <div v-else class="categories-container">
      <div
        v-for="category in categories"
        :key="category.industry"
        class="category-card"
      >
        <h3 class="category-title">{{ category.industry }}</h3>
        <div class="stock-list">
          <div
            v-for="stock in category.stocks"
            :key="stock.ticker"
            class="stock-item"
            @click="navigateToStock(stock.ticker)"
          >
            <span class="stock-code">{{ stock.ticker }}</span>
            <span class="stock-name">{{ stock.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { mapState, mapActions, mapGetters } from "vuex";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";

  export default {
    components: {
      LoadingSpinner,
      ErrorMessage,
    },
    computed: {
      ...mapState("stockApp", [
        "loading",
        "error",
        "stockData",
        "currentMarket",
      ]),
      ...mapGetters("stockApp", ["categories"]),
    },
    methods: {
      ...mapActions("stockApp", ["fetchStockCategories", "setCurrentMarket"]),
      navigateToStock(symbol) {
        localStorage.setItem("selectedMarket", "TW");

        this.$router.push({
          name: "StockAnalysis",
          params: { symbol },
          query: { market: "TW" },
        });
      },
      async fetchStockList() {
        try {
          await this.setCurrentMarket("TW");

          await this.fetchStockCategories({ force: true });

        } catch (error) {
          console.error("獲取台股列表失敗:", error);
        }
      },
    },
    created() {
      this.fetchStockList();
    },
  };
</script>

<style scoped>
.tw-stock-categories {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.categories-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.category-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.category-title {
  background: #4a6bff;
  color: white;
  padding: 15px;
  margin: 0;
  font-size: 18px;
}

.stock-list {
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s ease;
}

.stock-item:hover {
  background: #f5f8ff;
}

.stock-item:last-child {
  border-bottom: none;
}

.stock-code {
  font-weight: bold;
  color: #333;
}

.stock-name {
  color: #666;
}

@media (max-width: 768px) {
  .tw-stock-categories {
    padding: 15px;
  }
  
  .categories-container {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
}

.stock-list::-webkit-scrollbar {
  width: 8px;
}

.stock-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.stock-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.stock-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>