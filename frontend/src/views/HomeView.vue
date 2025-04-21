<template>
  <div class="profile-container">
    <div class="profile-card">
      <loading-spinner v-if="isLoading" />

      <!-- 用戶資訊區塊 -->
      <profile-header
        :email="userEmail"
        :registration-date="registrationDate"
      />

      <!-- 群組列表區塊 -->
      <groups-list
        :groups="groups"
        :selected-group="selectedGroup"
        :chart-data="chartData"
        @toggle-group="toggleGroup"
        @update-group-name="updateGroupName"
        @add-stock="addStock"
        @remove-stock="removeStock"
        @navigate="navigateToAnalysis"
      />

      <!-- 登出按鈕 -->
      <logout-button @click="handleLogout" />
    </div>

    <!-- 添加股票對話框 -->
    <add-stock-dialog
      :show="showAddDialog"
      :stock-list="stockList"
      @close="showAddDialog = false"
      @confirm="handleAddStock"
    />

    <confirm-dialog
      v-if="showLoginDialog"
      :title="'尚未登入'"
      :message="'您尚未登入或身分驗證已過期。是否前往登入頁面？'"
      :confirmText="'前往登入'"
      :cancelText="'返回股票分析'"
      @confirm="goToLogin"
      @cancel="goToStockAnalysis"
    />
  </div>
</template>

<script>
  import { isTokenExpired, clearAuthData, isGuestMode } from "@/utils/auth";
  import AddStockDialog from "@/components/tool/AddStockDialog.vue";
  import { cacheManager, CACHE_KEYS } from "@/services/cacheManager";
  import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
  import GroupsList from "@/components/profile/GroupsList.vue";
  import ProfileHeader from "@/components/profile/ProfileHeader.vue";
  import LogoutButton from "@/components/common/LogoutButton.vue";
  import ConfirmDialog from "@/components/common/ConfirmDialog.vue";

  export default {
    components: {
      AddStockDialog,
      LoadingSpinner,
      GroupsList,
      ProfileHeader,
      LogoutButton,
      ConfirmDialog,
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
        showLoginDialog: false,
        isSessionExpired: false,
        groupsUpdateInterval: null,
      };
    },
    async created() {
      await this.fetchStockList();

      if (isGuestMode()) {
        this.handleGuestMode();
        return;
      }
      
      // 先檢查 userId 是否有效
      if (!this.userId || this.userId === "undefined") {
        console.warn("Invalid user ID");
        this.isSessionExpired = false;
        this.showLoginDialog = true;
        return;
      }

      if (!isTokenExpired()) {
        await this.fetchGroups();
        await this.preloadAllChartData();
        this.startGroupsUpdateInterval();
      } else {
        this.isSessionExpired = true;
        this.handleTokenExpired();
      }
    },
    methods: {
      goToLogin() {
        this.showLoginDialog = false;
        this.$router.push("/");
      },
      goToStockAnalysis() {
        this.showLoginDialog = false;
        this.$router.push("/stock-app");
      },
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

        if (this.isSessionExpired) {
          this.$router.push("/");
          console.warn("Session expired. Please login again.");
        } else {
          // 如果是未登入，顯示對話框
          this.showLoginDialog = true;
        }
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
        this.groups.forEach((group) => {
          group.stocks.forEach((stock) => allStocks.add(stock));
        });

        const stocksArray = Array.from(allStocks);
        const batchSize = 5; // 每批次處理5個股票
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
      handleGuestMode() {
        // 訪客體驗
        this.groups = [
          {
            name: "訪客範例群組",
            stocks: ["AAPL", "MSFT", "TSLA", "GOOGL"],
          },
        ];
        this.selectedGroup = 0;
        this.batchLoadChartData();
      },
    },
    beforeMount() {
      // 檢查是否為訪客模式，如果是則總是顯示登入對話框
      if (isGuestMode()) {
        this.showLoginDialog = true;
        return;
      }
    },
    // 組件銷毀時檢查快取
    beforeUnmount() {
      if (this.groupsUpdateInterval) {
        clearInterval(this.groupsUpdateInterval);
        this.groupsUpdateInterval = null;
      }

      cacheManager.checkAndCleanCache();
    },
    errorCaptured(err, vm, info) {
      console.error(`Error in HomeView: ${err.toString()}\nInfo: ${info}`);
      // 確保清理 interval 即使在錯誤發生時
      if (this.groupsUpdateInterval) {
        clearInterval(this.groupsUpdateInterval);
      }
      return false; // 防止錯誤繼續傳播
    },
  };
</script>

<style scoped>
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

  @media (max-width: 768px) {
    .profile-container {
      padding: 20px;
    }

    .profile-card {
      padding: 20px;
    }
  }
</style>
