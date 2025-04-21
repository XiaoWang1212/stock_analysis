<template>
  <div class="moving-avg-chart">
    <div class="chart-header">
      <button @click="goBack" class="back-btn">
        <span class="material-icons">arrow_back</span>
        返回
      </button>
      <div class="add-to-group">
        <LoadingSpinner v-if="loading" />
        <ErrorMessage v-else-if="error" :message="error" @retry="fetchGroups" />
        <template v-else>
          <select v-model="selectedGroup" class="group-select">
            <option value="" disabled>選擇群組</option>
            <option
              v-for="(group, index) in groups"
              :key="index"
              :value="index"
            >
              {{ group.name || `群組 ${index + 1}` }}
            </option>
          </select>
          <button
            @click="addToGroup"
            class="add-btn"
            :disabled="selectedGroup === ''"
          >
            <span class="material-icons">add</span>
            加入群組
          </button>
        </template>
      </div>
    </div>
    <h2>
      {{ symbol }} {{ effectiveMarket === "TW" ? `(${getStockName() || '台股'})` : "" }} 技術分析
    </h2>

    <div class="chart-selector">
      <label> <input type="checkbox" v-model="showSMA" /> SMA </label>
      <label> <input type="checkbox" v-model="showEMA" /> EMA </label>
      <label> <input type="checkbox" v-model="showWMA" /> WMA </label>
      <label> <input type="checkbox" v-model="showKAMA" /> KAMA </label>
    </div>
    <div class="chart-container">
      <SMAChart v-if="showSMA" :symbol="symbol" :market="effectiveMarket" />
      <EMAChart v-if="showEMA" :symbol="symbol" :market="effectiveMarket" />
      <WMAChart v-if="showWMA" :symbol="symbol" :market="effectiveMarket" />
      <KAMAChart v-if="showKAMA" :symbol="symbol" :market="effectiveMarket" />
      <div class="analysis-selector">
        <button
          @click="selectAnalysis('BIAS')"
          :class="{ active: selectedAnalysis === 'BIAS' }"
        >
          BIAS
        </button>
        <button
          @click="selectAnalysis('RSI')"
          :class="{ active: selectedAnalysis === 'RSI' }"
        >
          RSI
        </button>
        <button
          @click="selectAnalysis('STOCH')"
          :class="{ active: selectedAnalysis === 'STOCH' }"
        >
          STOCH
        </button>
        <button
          @click="selectAnalysis('STOCHRSI')"
          :class="{ active: selectedAnalysis === 'STOCHRSI' }"
        >
          STOCH RSI
        </button>
        <button
          @click="selectAnalysis('STOCHF')"
          :class="{ active: selectedAnalysis === 'STOCHF' }"
        >
          STOCH F
        </button>
        <button
          @click="selectAnalysis('MACD')"
          :class="{ active: selectedAnalysis === 'MACD' }"
        >
          MACD
        </button>
      </div>
      <div class="analysis-container">
        <SMAAndBIASChart
          v-if="selectedAnalysis === 'BIAS'"
          :symbol="symbol"
          :market="effectiveMarket"
        />
        <RSIChart
          v-else-if="selectedAnalysis === 'RSI'"
          :symbol="symbol"
          :market="effectiveMarket"
        />
        <STOCHChart
          v-else-if="selectedAnalysis === 'STOCH'"
          :symbol="symbol"
          :market="effectiveMarket"
        />
        <STOCHRSIChart
          v-else-if="selectedAnalysis === 'STOCHRSI'"
          :symbol="symbol"
          :market="effectiveMarket"
        />
        <STOCHFChart
          v-else-if="selectedAnalysis === 'STOCHF'"
          :symbol="symbol"
          :market="effectiveMarket"
        />
        <MACDChart
          v-else-if="selectedAnalysis === 'MACD'"
          :symbol="symbol"
          :market="effectiveMarket"
        />
      </div>
    </div>
  </div>
</template>

<script>
  import SMAChart from "./movingAvg/SMAChart.vue";
  import EMAChart from "./movingAvg/EMAChart.vue";
  import WMAChart from "./movingAvg/WMAChart.vue";
  import KAMAChart from "./movingAvg/KAMAChart.vue";
  import SMAAndBIASChart from "./movingAvg/SMAAndBIASChart.vue";
  import RSIChart from "./momentum/RSIChart.vue";
  import STOCHChart from "./momentum/STOCHChart.vue";
  import STOCHRSIChart from "./momentum/STOCHRSIChart.vue";
  import STOCHFChart from "./momentum/STOCHFChart.vue";
  import MACDChart from "./momentum/MACDChart.vue";

  import { isTokenExpired } from "@/utils/auth";
  import { mapState } from "vuex";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";

  export default {
    components: {
      SMAChart,
      EMAChart,
      WMAChart,
      KAMAChart,
      SMAAndBIASChart,
      RSIChart,
      STOCHChart,
      STOCHRSIChart,
      STOCHFChart,
      MACDChart,
      LoadingSpinner,
      ErrorMessage,
    },
    props: {
      symbol: {
        type: String,
        required: true,
      },
      market: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        showSMA: true,
        showEMA: false,
        showWMA: false,
        showKAMA: false,
        selectedAnalysis: "BIAS",
        selectedGroup: "",
        groups: [],
        loading: false,
        error: null,
        fetchError: null,
      };
    },
    computed: {
      ...mapState("stockApp", {
        twStockNameMap: (state) => state.twStockNameMap, 
      }),
      
      effectiveMarket() {
        if (this.market && (this.market === "US" || this.market === "TW")) {
          return this.market;
        }

        const storedMarket = localStorage.getItem("selectedMarket");
        if (storedMarket && (storedMarket === "US" || storedMarket === "TW")) {
          return storedMarket;
        }

        return this.market || "US"; // 如果都沒有，默認使用美股
      },

      marketName() {
        return this.effectiveMarket === "TW" ? "台股" : "美股";
      },
    },
    async created() {
      await this.fetchGroups();

      if (this.effectiveMarket === "TW") {
        await this.loadTwStockNameMap();
      }
    },
    methods: {
      goBack() {
        this.$router.push({
          name: "StockAnalysis",
          params: { symbol: this.symbol },
          query: { keepData: "true", market: this.effectiveMarket },
        });
      },
      // 監聽瀏覽器的後退按鈕
      handleBrowserBack() {
        window.addEventListener("popstate", () => {
          // 在用戶點擊瀏覽器的後退按鈕時執行相同邏輯
          const symbol = this.symbol;
          if (symbol) {
            this.$router.replace({
              name: "StockAnalysis",
              params: { symbol: this.symbol },
              query: { market: this.effectiveMarket },
            });
          }
        });
      },
      selectAnalysis(analysis) {
        this.selectedAnalysis = analysis;
      },
      async fetchGroups() {
        const userId = localStorage.getItem("userId");
        if (!userId) {
          this.error = "請先登入";
          return;
        }

        if (isTokenExpired()) {
          this.error = "登入已過期，請重新登入";
          return;
        }

        this.loading = true;
        try {
          const response = await fetch(
            `http://localhost:5000/groups/${userId}`,
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${sessionStorage.getItem("token")}`,
              },
            }
          );

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          this.groups = data.groups;
        } catch (error) {
          console.error("Error fetching groups:", error);
          this.error = "無法載入群組資料";
        } finally {
          this.loading = false;
        }
      },
      async addToGroup() {
        if (this.selectedGroup === "") return;

        const userId = localStorage.getItem("userId");
        if (!userId) return;

        try {
          const currentStocks = [...this.groups[this.selectedGroup].stocks];

          // 檢查是否已存在
          if (currentStocks.includes(this.symbol)) {
            alert("此股票已在群組中");
            return;
          }

          const response = await fetch(
            `http://localhost:5000/groups/${userId}`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${sessionStorage.getItem("token")}`,
              },
              body: JSON.stringify({
                index: this.selectedGroup,
                stocks: [...currentStocks, this.symbol],
              }),
            }
          );

          if (response.ok) {
            alert("成功加入群組！");
            // 更新本地群組數據
            this.groups[this.selectedGroup].stocks.push(this.symbol);
          } else {
            alert("加入群組失敗，請稍後再試");
          }
        } catch (error) {
          console.error("Error adding stock to group:", error);
          alert("加入群組時發生錯誤");
        }
      },
      getStockName() {
        if (this.effectiveMarket === "TW" && this.twStockNameMap) {
          // 返回該股票的中文名稱
          return this.twStockNameMap[this.symbol] || "";
        }
        return ""; // 如果是美股或沒有找到名稱，返回空字符串
      },
      async loadTwStockNameMap() {
        try {
          // 檢查是否已經有台股名稱映射
          if (!this.twStockNameMap || Object.keys(this.twStockNameMap).length === 0) {
            await this.$store.dispatch("stockApp/generateTwStockNameMap");
          }
        } catch (error) {
          console.error("載入台股名稱映射時出錯:", error);
        }
      },
    },
    mounted() {
      this.handleBrowserBack();
    },
    beforeUnmount() {
      window.removeEventListener("popstate", this.handleBrowserBack);
    },
  };
</script>

<style scoped>
  .moving-avg-chart {
    padding: 20px;
    font-family: Arial, sans-serif;
  }

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .back-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 16px;
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
  }

  .back-btn:hover {
    background: #5a6268;
  }

  .add-to-group {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .group-select {
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
    font-size: 14px;
    min-width: 150px;
  }

  .add-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 16px;
    background: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
  }

  .add-btn:hover {
    background: #357abd;
  }

  .add-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .material-icons {
    font-size: 18px;
  }

  .chart-selector {
    margin-bottom: 20px;
  }

  .chart-selector label {
    margin-right: 10px;
  }

  .chart-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .analysis-selector {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }

  .analysis-selector button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s;
    margin: 0 5px;
  }

  .analysis-selector button.active {
    background-color: #0056b3;
  }

  .analysis-selector button:hover {
    background-color: #0056b3;
  }

  .analysis-container {
    margin-top: 20px;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.5s;
  }

  .fade-enter,
  .fade-leave-to {
    opacity: 0;
  }
</style>
