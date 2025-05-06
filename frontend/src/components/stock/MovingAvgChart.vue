<template>
  <div class="moving-avg-chart">
    <div class="chart-header">
      <button @click="goBack" class="back-btn">返回</button>
      <div class="material-icons">arrow_back</div>
      <h1>技術分析</h1>
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

    <div class="chart-container">
      <h2>
        {{ symbol }} {{ effectiveMarket === "TW" ? `- ${getStockName() || '台股'}` : "" }} 
      </h2>

      <div class="chart-selector">
        <!--
        <label> <input type="checkbox" v-model="showSMA" /> SMA </label>
        <label> <input type="checkbox" v-model="showEMA" /> EMA </label>
        <label> <input type="checkbox" v-model="showWMA" /> WMA </label>
        <label> <input type="checkbox" v-model="showKAMA" /> KAMA </label>
        -->
        <div class="chart-selector-button" 
          @click="toggle_chart('showSMA')" 
          :class="{'chart-selector-button-click' : showSMA}"
          >SMA
        </div>
        <div class="chart-selector-button" 
          @click="toggle_chart('showEMA')" 
          :class="{'chart-selector-button-click' : showEMA}"
          >EMA
        </div>
        <div class="chart-selector-button" 
          @click="toggle_chart('showWMA')" 
          :class="{'chart-selector-button-click' : showWMA}"
          >WMA
        </div>
        <div class="chart-selector-button" 
          @click="toggle_chart('showKAMA')" 
          :class="{'chart-selector-button-click' : showKAMA}"
          >KAMA
        </div>
      </div>
      <div class="chart-container">
        <SMAChart v-if="showSMA" :symbol="symbol" :market="effectiveMarket" />
        <EMAChart v-if="showEMA" :symbol="symbol" :market="effectiveMarket" />
        <WMAChart v-if="showWMA" :symbol="symbol" :market="effectiveMarket" />
        <KAMAChart v-if="showKAMA" :symbol="symbol" :market="effectiveMarket" />
        <div class="analysis-selector">
          <div class="analysis-selector-button"
            @click="selectAnalysis('BIAS')"
            :class="{ 'analysis-selector-button-click': selectedAnalysis === 'BIAS' }"
          >
            BIAS
          </div>
          <div class="analysis-selector-button"
            @click="selectAnalysis('RSI')"
            :class="{ 'analysis-selector-button-click': selectedAnalysis === 'RSI' }"
          >
            RSI
          </div>
          <div class="analysis-selector-button"
            @click="selectAnalysis('STOCH')"
            :class="{ 'analysis-selector-button-click': selectedAnalysis === 'STOCH' }"
          >
            STOCH
          </div>
          <div class="analysis-selector-button"
            @click="selectAnalysis('STOCHRSI')"
            :class="{ 'analysis-selector-button-click': selectedAnalysis === 'STOCHRSI' }"
          >
            STOCH RSI
          </div>
          <div class="analysis-selector-button"
            @click="selectAnalysis('STOCHF')"
            :class="{ 'analysis-selector-button-click': selectedAnalysis === 'STOCHF' }"
          >
            STOCH F
          </div>
          <div class="analysis-selector-button"
            @click="selectAnalysis('MACD')"
            :class="{ 'analysis-selector-button-click': selectedAnalysis === 'MACD' }"
          >
            MACD
          </div>
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
      toggle_chart (key){
        this[key] = !this[key];
      }
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
    display: grid;
    grid-template-columns: 20% 60% 20%;
    justify-content: center;
    align-items: center;
    margin: 20px;
    margin-top: 0;
  }

  .back-btn {
    width: 80px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px 16px;
    background: #5B5B5B;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
  }

  .back-btn:hover {
    background: #66B3FF;
  }

  .add-to-group {
    display: flex;
    justify-content: end;
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

  .chart-container{
    background-color: #4F4F4F;
    border-radius: 8px;
    padding-bottom: 20px;
  }

  h2{
    padding-bottom: 20px;
    margin-bottom: 0;
    border-bottom: 2px solid #7B7B7B;
  }

  h1{
    color: white;
    padding-bottom: 10px;
    border-bottom: 2px solid white;
    margin-bottom: 30px;
  }

  .chart-selector{
    display: grid;
    grid-template-columns: repeat(4, 25%);
    text-align: center;
  }

  .chart-selector-button{
    background-color: #5B5B5B;
    border-radius: 8px;
    padding: 10px 20px;
    margin: 0 10px;
    cursor: pointer;
  }

  .chart-selector-button-click{
    background-color: #66B3FF;
  }

  /*.chart-selector label {
    padding: 10px;
    margin-right: 10px;
  }*/

  .chart-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .analysis-selector {
    display: grid;
    grid-template-columns: repeat(6, 16.7%);
    justify-content: center;
    text-align: center;
    margin-top: 20px;
  }

  .analysis-selector-button {
    padding: 10px 20px;
    background-color: #5B5B5B;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s;
    margin: 0 10px;
  }

  .analysis-selector-button-click{
    background-color: #66B3FF;
  }

  .analysis-container {
    margin-top: 40px;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.5s;
  }

  .fade-enter,
  .fade-leave-to {
    opacity: 0;
  }

  .material-icons {
    display: none;
    padding: 8px;
    width: 30px;
    height: 30px;
    line-height: 30px;
    background: #5B5B5B;
    color: white;
    border: none;
    border-radius: 100%;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
  }

  .material-icons:hover {
    background: #66B3FF;
    transform: scale(1);
  }

  @media (max-width: 950px){
    .analysis-selector{
      grid-template-columns: repeat(3, 31%);
      gap: 20px;
    }
  }

  @media (max-width: 520px){
    .chart-selector{
      grid-template-columns: repeat(2, 47%);
      gap: 20px;
    }
    .analysis-selector{
      grid-template-columns: repeat(2, 47%);
      gap: 20px;
    }
    .material-icons {
      display: block;
    }
    .back-btn{
      display: none;
    }
  }
</style>
