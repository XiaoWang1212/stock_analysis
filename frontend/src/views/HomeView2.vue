<template>
  <div class="profile-container">
    <div class="profile-card">
      <!-- 用戶基本資訊區塊 -->
      <div v-if="isLoading" class="loading-overlay">
        <loading-spinner />
      </div>
      <div class="profile-section">
        <div class="profile-header">
          <span class="material-icons profile-icon">account_circle</span>
          <h2>個人資料</h2>
        </div>

        <div class="profile-info">
          <div class="info-item">
            <span class="label">電子信箱</span>
            <span class="value">{{ userEmail }}</span>
          </div>
          <div class="info-item">
            <span class="label">註冊日期</span>
            <span class="value">{{ registrationDate }}</span>
          </div>
        </div>
      </div>

      <!-- 股票群組區塊 -->
      <div class="groups-section">
        <div class="groups-header">
          <h3>股票群組管理</h3>
          <p class="groups-description">您可以創建最多6個群組來管理您的股票</p>
        </div>

        <div class="groups-container">
          <!-- 遮罩層 -->
          <div
            v-if="selectedGroup !== null"
            class="overlay"
            @click="toggleGroup(null)"
          ></div>

          <div
            v-for="(group, index) in groups"
            :key="index"
            class="group-card"
            :class="{ expanded: selectedGroup === index }"
            @click="(e) => toggleGroup(index, e)"
          >
            <div class="expand-handle">
              <span class="material-icons">{{
                selectedGroup === index ? "expand_less" : "expand_more"
              }}</span>
            </div>

            <div class="group-content">
              <div class="group-header">
                <input
                  v-model="group.name"
                  @change="updateGroupName(index, group.name)"
                  class="group-name-input"
                  :placeholder="`群組 ${index + 1}`"
                  @click.stop
                />
                <button @click.stop="addStock(index)" class="add-stock-btn">
                  <span class="material-icons">add</span>
                  添加股票
                </button>
              </div>

              <div
                v-if="group.stocks.length > 0 && selectedGroup !== index"
                class="stocks-list"
              >
                <div
                  v-for="stock in group.stocks"
                  :key="stock"
                  class="stock-item"
                  @click.stop="navigateToAnalysis(stock)"
                >
                  <div class="stock-info">
                    <span class="stock-code">
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
                    @click.stop="removeStock(index, stock)"
                  >
                    <span class="material-icons">close</span>
                  </button>
                </div>
              </div>

              <div v-if="selectedGroup === index" class="charts-grid">
                <div
                  v-for="stock in group.stocks"
                  :key="stock"
                  class="stock-chart-item"
                  @click.stop="navigateToAnalysis(stock)"
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
                  <mini-stock-chart
                    v-if="chartData[stock]"
                    :chartData="chartData[stock]"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <button class="logout-btn" @click="handleLogout">
        <span class="material-icons">logout</span>
        登出
      </button>
    </div>
    <add-stock-dialog
      :show="showAddDialog"
      :stock-list="stockList"
      @close="showAddDialog = false"
      @confirm="handleAddStock"
    />
  </div>
</template>

<script>
  import { isTokenExpired, clearAuthData } from "@/utils/auth";
  import MiniStockChart from "@/components/stock/MiniStockChart.vue";
  import AddStockDialog from "@/components/tool/AddStockDialog.vue";
  import { cacheManager, CACHE_KEYS } from "@/services/cacheManager";
  import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

  export default {
    components: {
      MiniStockChart,
      AddStockDialog,
      LoadingSpinner,
    },
    data() {
      return {
        userEmail: localStorage.getItem("userEmail") || "未登入",
        registrationDate: localStorage.getItem("registrationDate") || "無資料",
        userId: localStorage.getItem("userId"),
        groups: [],
        selectedGroup: null,
        chartData: {},
        showAddDialog: false,
        stockList: [],
        currentGroupIndex: null,
        isLoading: false,
        loadedStocks: new Set(), // 追蹤已載入的股票
      };
    },
    async created() {
      await this.fetchStockList();

      // 先檢查 userId 是否有效
      if (!this.userId || this.userId === "undefined") {
        console.warn("Invalid user ID");
        this.handleTokenExpired();
        return;
      }

      if (!isTokenExpired()) {
        await this.fetchGroups();
        await this.preloadAllChartData();
        this.startGroupsUpdateInterval();
      } else {
        this.handleTokenExpired();
      }
    },
    methods: {
      startGroupsUpdateInterval() {
        this.groupsUpdateInterval = setInterval(async () => {
          await this.fetchGroups();
        }, 60 * 60 * 1000);
      },
      async preloadAllChartData() {
        for (const group of this.groups) {
          for (const stock of group.stocks) {
            await new Promise((resolve) => setTimeout(resolve, 1000));
            await this.getChartData(stock);
          }
        }
      },
      async toggleGroup(index, event) {
        if (this.selectedGroup === index) {
          const card = event?.target?.closest(".group-card");
          if (card) {
            card.classList.add("collapsing");
            setTimeout(() => {
              this.selectedGroup = null;
              card.classList.remove("collapsing");
            }, 300);
          } else {
            this.selectedGroup = null;
          }
        } else {
          if (event) {
            const card = event.target.closest(".group-card");
            if (card) {
              const rect = card.getBoundingClientRect();
              card.style.setProperty("--original-width", `${rect.width}px`);
              card.style.setProperty("--original-height", `${rect.height}px`);
              card.style.setProperty("--original-top", `${rect.top}px`);
              card.style.setProperty("--original-left", `${rect.left}px`);
            }
          }
          this.selectedGroup = index;
        }
      },
      handleTokenExpired() {
        clearAuthData();
        this.$router.push("/");
        console.warn("Session expired. Please login again.");
      },
      async fetchGroups() {
        this.isLoading = true;
        try {
          if (!this.userId || this.userId === "undefined") {
            throw new Error("Invalid user ID");
          }

          if (isTokenExpired()) {
            this.handleTokenExpired();
            return;
          }

          const cacheKey = CACHE_KEYS.USER_GROUPS + this.userId;
          const cachedGroups = cacheManager.getCache(cacheKey);

          if (cachedGroups) {
            console.log("Using cached groups data");
            this.groups = cachedGroups;
            await this.batchLoadChartData(); 
            this.isLoading = false;
            return;
          }

          const response = await fetch(
            `http://localhost:5000/groups/${this.userId}`,
            {
              headers: {
                Authorization: `Bearer ${sessionStorage.getItem("token")}`,
                "Content-Type": "application/json",
              },
            }
          );

          if (response.status === 401) {
            this.handleTokenExpired();
            return;
          }

          const data = await response.json();
          if (response.ok) {
            this.groups = data.groups;
            await this.batchLoadChartData();
            cacheManager.setCache(cacheKey, data.groups);
          } else {
            console.error(data.error);
          }
        } catch (error) {
          console.error("Error fetching groups:", error);
        } finally {
          this.isLoading = false;
        }
      },
      async updateGroupName(index, name) {
        if (isTokenExpired()) {
          this.handleTokenExpired();
          return;
        }

        try {
          const response = await fetch(
            `http://localhost:5000/groups/${this.userId}`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${sessionStorage.getItem("token")}`,
              },
              body: JSON.stringify({ index, name }),
            }
          );

          if (response.status === 401) {
            this.handleTokenExpired();
            return;
          }

          const data = await response.json();

          if (response.ok) {
            this.groups = data.groups;
            // 確保每個群組都有 stocks 陣列
            this.groups = this.groups.map((group) => ({
              ...group,
              stocks: group.stocks || [],
            }));
            await this.preloadAllChartData();
            this.$forceUpdate(); // 強制更新視圖
          } else {
            console.error(data.error);
          }
        } catch (error) {
          console.error("Error updating group name:", error);
        }
      },
      async fetchStockList() {
        try {
          const response = await fetch(
            "http://127.0.0.1:5000/stock_app/api/categories"
          );
          const data = await response.json();
          this.stockList = data.map((item) => item.ticker).filter(Boolean);
        } catch (error) {
          console.error("Error fetching stock list:", error);
        }
      },
      addStock(index) {
        this.currentGroupIndex = index;
        this.showAddDialog = true;
      },
      async handleAddStock(stock) {
        if (isTokenExpired()) {
          this.handleTokenExpired();
          return;
        }

        const index = this.currentGroupIndex;
        if (stock) {
          try {
            const currentStocks = [...this.groups[index].stocks];

            if (currentStocks.includes(stock)) {
              alert("此股票已在群組中");
              return;
            }

            // 先取得股票數據
            try {
              const stockResponse = await fetch(
                `http://localhost:5000/stock_app/api/stock_data/${stock}`
              );
              const stockData = await stockResponse.json();

              // 儲存到快取
              const cacheKey = CACHE_KEYS.STOCK_DATA + stock;
              cacheManager.setCache(cacheKey, stockData);

              // 更新股票數據
              this.chartData = {
                ...this.chartData,
                [stock]: {
                  ...stockData,
                  change: stockData.change,
                },
              };

              // 更新群組
              const response = await fetch(
                `http://localhost:5000/groups/${this.userId}`,
                {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${sessionStorage.getItem("token")}`,
                  },
                  body: JSON.stringify({
                    index,
                    stocks: [...currentStocks, stock],
                  }),
                }
              );

              if (response.status === 401) {
                this.handleTokenExpired();
                return;
              }

              if (response.ok) {
                // 更新本地數據
                this.groups[index].stocks = [...currentStocks, stock];

                // 強制更新視圖
                await this.$nextTick();
                this.$forceUpdate();
              }
            } catch (error) {
              console.error(`Error fetching data for stock ${stock}:`, error);
            }
          } catch (error) {
            console.error("Error adding stock:", error);
          }
        }
      },
      handleLogout() {
        clearAuthData();
        this.$router.push("/");
      },
      async removeStock(index, stock) {
        if (isTokenExpired()) {
          this.handleTokenExpired();
          return;
        }

        try {
          const currentStocks = [...this.groups[index].stocks];
          const newStocks = currentStocks.filter((s) => s !== stock);

          const response = await fetch(
            `http://localhost:5000/groups/${this.userId}`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${sessionStorage.getItem("token")}`,
              },
              body: JSON.stringify({ index, stocks: newStocks }),
            }
          );

          if (response.status === 401) {
            this.handleTokenExpired();
            return;
          }

          const data = await response.json();
          if (response.ok) {
            this.groups[index].stocks = newStocks;
          } else {
            console.error(data.error);
          }
        } catch (error) {
          console.error("Error removing stock:", error);
        }
      },
      navigateToAnalysis(symbol) {
        this.$router.push(`/moving-avg/${symbol}`);
      },
      async getChartData(symbol) {
        if (!this.chartData[symbol]) {
          // 檢查快取
          const cacheKey = CACHE_KEYS.STOCK_DATA + symbol;
          const cachedData = cacheManager.getCache(cacheKey);

          if (cachedData) {
            console.log(`Using cached data for ${symbol}`);
            this.chartData[symbol] = cachedData;
            return cachedData;
          }

          try {
            const response = await fetch(
              `http://localhost:5000/stock_app/api/stock_data/${symbol}`,
              {
                method: "GET",
                headers: {
                  "Content-Type": "application/json",
                  Authorization: `Bearer ${sessionStorage.getItem("token")}`,
                },
              }
            );
            const data = await response.json();

            // 儲存到快取
            cacheManager.setCache(cacheKey, data);
            this.chartData[symbol] = data;
            return data;
          } catch (error) {
            console.error("Error fetching chart data:", error);
          }
        }
        return this.chartData[symbol];
      },

      // 添加清理快取方法
      clearStockDataCache() {
        Object.keys(this.chartData).forEach((symbol) => {
          const cacheKey = CACHE_KEYS.STOCK_DATA + symbol;
          localStorage.removeItem(cacheKey);
        });
        this.chartData = {};
      },

      // 新增批次載入方法
      async batchLoadChartData() {
        const allStocks = new Set();
        this.groups.forEach(group => {
          group.stocks.forEach(stock => allStocks.add(stock));
        });

        const stocksArray = Array.from(allStocks);
        const batchSize = 5;  // 每批次處理5個股票
        const batches = [];

        // 將股票分組
        for (let i = 0; i < stocksArray.length; i += batchSize) {
          batches.push(stocksArray.slice(i, i + batchSize));
        }

        // 暫存所有數據
        const tempChartData = {};

        // 批次處理
        for (const batch of batches) {
          await Promise.all(
            batch.map(async (stock) => {
              const data = await this.fetchStockData(stock);
              if (data) {
                tempChartData[stock] = data;
              }
            })
          );
        }

        // 一次性更新視圖
        this.chartData = { ...tempChartData };
      },

      // 優化股票數據獲取
      async fetchStockData(symbol) {
        const cacheKey = CACHE_KEYS.STOCK_DATA + symbol;
        const cachedData = cacheManager.getCache(cacheKey);

        if (cachedData) {
          return cachedData;
        }

        try {
          const response = await fetch(
            `http://localhost:5000/stock_app/api/stock_data/${symbol}`,
            {
              method: "GET",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${sessionStorage.getItem("token")}`,
              },
            }
          );
          const data = await response.json();
          cacheManager.setCache(cacheKey, data);
          return data;
        } catch (error) {
          console.error(`Error fetching data for ${symbol}:`, error);
          return null;
        }
      },
    },

    // 組件銷毀時檢查快取
    beforeUnmount() {
      if (this.groupsUpdateInterval) {
        clearInterval(this.groupsUpdateInterval);
      }
      cacheManager.checkAndCleanCache();
    },
  };
</script>

<style scoped>
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }

  .profile-container {
    min-height: calc(100vh - 60px);
    padding: 40px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }

  .profile-card {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    padding: 40px;
  }

  .profile-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 25px;
  }

  .profile-header h2 {
    font-size: 1.8em;
    color: #2c3e50;
    margin: 0;
  }

  .profile-section {
    margin-bottom: 40px;
    padding-bottom: 20px;
    border-bottom: 2px solid #eee;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
  }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: 998;
    animation: fadeIn 0.3s ease;
  }

  .groups-header {
    margin-bottom: 30px;
    text-align: center;
  }

  .groups-header h3 {
    font-size: 1.5em;
    margin-bottom: 10px;
  }

  .groups-description {
    color: #666;
    font-size: 1em;
    margin-top: 5px;
  }

  .groups-container {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: repeat(3, auto);
    gap: 25px;
    margin-bottom: 40px;
    position: relative;
    width: 100%;
  }

  .group-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    gap: 10px;
  }

  .group-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e9ecef;
    min-height: 200px;
    cursor: pointer;
    width: auto;
    box-sizing: border-box;
    position: relative;
    z-index: 1;
    transform-origin: top left;
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
    overflow-y: auto;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    isolation: isolate;
    animation: expandFromOrigin 0.3s ease-out forwards;
  }

  .group-card.collapsing {
    animation: collapseToOrigin 0.3s ease-out forwards;
  }

  .group-card:not(.expanded):hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .group-card.expanded .close-btn {
    position: absolute;
    top: 20px;
    right: 20px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
  }

  .expanded .group-header {
    margin-bottom: 30px;
  }

  .group-content {
    transition: all 0.3s ease;
  }

  .expanded-content {
    padding: 20px;
    height: calc(90vh - 100px);
    overflow-y: auto;
  }

  .profile-icon {
    font-size: 48px;
    color: #4a90e2;
  }

  .profile-info {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 30px;
  }

  .group-name-input {
    font-size: 1em;
    color: #2c3e50;
    background: white;
    transition: border-color 0.3s ease;
  }

  .group-name-input:focus {
    border-color: #4a90e2;
    outline: none;
  }

  .add-stock-btn:hover {
    background: #357abd;
    transform: translateY(-1px);
    transition: all 0.3s ease;
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
    font-size: 1em;
    transition: all 0.3s ease;
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

  .stocks-list::-webkit-scrollbar {
    width: 6px;
  }

  .stocks-list::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  .stocks-list::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }

  .stocks-list::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }

  .expanded .stocks-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-top: 30px;
    transition: none;
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

  .stock-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .stock-item:hover .stock-code {
    color: #4a90e2;
  }

  /* 移除未展開時的圖表相關樣式 */
  .mini-chart-container {
    display: none; /* 或完全移除這個樣式 */
  }

  .expanded .stock-item {
    padding: 15px 20px;
    font-size: 1.1em;
    transform: none;
    transition: none;
  }

  .stock-code,
  .stock-change {
    display: flex;
    align-items: center;
    font-size: 0.95em;
  }

  .stock-code {
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
    min-width: 60px;
    text-align: right;
  }

  .positive {
    color: #4caf50;
  }

  .negative {
    color: #f44336;
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
    color: #999;
    text-align: center;
    padding: 20px 0;
    font-size: 0.9em;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 2px dashed #e0e0e0;
    margin-top: 15px;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #eee;
  }

  .label {
    color: #666;
    font-weight: 500;
  }

  .value {
    color: #333;
  }

  .logout-btn {
    max-width: 300px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: #ff4d4d;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    margin: 30px auto 0;
    padding: 15px;
    position: relative;
  }

  .logout-btn:hover {
    background: #ff3333;
  }

  .logout-btn .material-icons {
    font-size: 20px;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes expandFromOrigin {
    0% {
      transform: translate(0, 0) scale(1);
      width: var(--original-width);
      height: var(--original-height);
      top: var(--original-top);
      left: var(--original-left);
    }
    100% {
      transform: translate(-50%, -50%) scale(1);
      width: 90vw;
      height: 90vh;
      top: 50%;
      left: 50%;
    }
  }

  @keyframes collapseToOrigin {
    0% {
      transform: translate(-50%, -50%) scale(1);
      width: 90vw;
      height: 90vh;
      top: 50%;
      left: 50%;
    }
    100% {
      transform: translate(0, 0) scale(1);
      width: var(--original-width);
      height: var(--original-height);
      top: var(--original-top);
      left: var(--original-left);
    }
  }

  @media (max-width: 768px) {
    .profile-container {
      padding: 20px;
    }

    .profile-card {
      padding: 20px;
    }

    .groups-container {
      grid-template-columns: 1fr;
    }

    .group-card {
      min-height: 180px;
    }

    .group-card.expanded {
      width: 95vw;
      height: 95vh;
      padding: 20px;
    }

    .profile-header h2 {
      font-size: 1.5em;
    }
  }

  .expanded-content {
    margin-top: 20px;
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
    justify-content: space-between;
  }

  .stock-chart-item .stock-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
    height: auto;
    min-height: 24px;
  }

  .stock-chart-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
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
    overflow: hidden;
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

  .stock-symbol {
    font-size: 1.1em;
    font-weight: 600;
    color: #2c3e50;
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

  .expand-handle {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.05);
    transition: background 0.2s;
  }

  .expand-handle:hover {
    background: rgba(0, 0, 0, 0.1);
  }

  .stock-chart-item {
    cursor: pointer;
    transition: transform 0.2s;
  }

  .stock-chart-item .stock-symbol {
    font-size: 1.1em;
    font-weight: 600;
    color: #2c3e50;
    margin-right: auto;
  }

  .stock-chart-item .stock-change {
    font-size: 1em;
    min-width: 80px;
    text-align: right;
  }

  .stock-chart-item .stock-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 8px;
    padding-bottom: 0;
    border-bottom: none;
    height: auto;
    min-height: 24px;
  }

  .stock-chart-item:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    transform: none;
  }

  .group-card {
    position: relative;
  }

  /* 確保其他互動元素不會觸發展開/收合 */
  .group-name-input,
  .add-stock-btn,
  .remove-stock-btn {
    pointer-events: auto;
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
</style>
