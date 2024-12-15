<template>
  <div class="moving-avg-chart">
    <h2>{{ symbol }} Moving Averages Chart</h2>
    <div class="chart-header">
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

    <div class="chart-selector">
      <label> <input type="checkbox" v-model="showSMA" /> SMA </label>
      <label> <input type="checkbox" v-model="showEMA" /> EMA </label>
      <label> <input type="checkbox" v-model="showWMA" /> WMA </label>
      <label> <input type="checkbox" v-model="showKAMA" /> KAMA </label>
    </div>
    <div class="chart-container">
      <SMAChart v-if="showSMA" :symbol="symbol" />
      <EMAChart v-if="showEMA" :symbol="symbol" />
      <WMAChart v-if="showWMA" :symbol="symbol" />
      <KAMAChart v-if="showKAMA" :symbol="symbol" />
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
        <SMAAndBIASChart v-if="selectedAnalysis === 'BIAS'" :symbol="symbol" />
        <RSIChart v-else-if="selectedAnalysis === 'RSI'" :symbol="symbol" />
        <STOCHChart v-else-if="selectedAnalysis === 'STOCH'" :symbol="symbol" />
        <STOCHRSIChart
          v-else-if="selectedAnalysis === 'STOCHRSI'"
          :symbol="symbol"
        />
        <STOCHFChart
          v-else-if="selectedAnalysis === 'STOCHF'"
          :symbol="symbol"
        />
        <MACDChart v-else-if="selectedAnalysis === 'MACD'" :symbol="symbol" />
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
      };
    },
    async created() {
      await this.fetchGroups();
    },
    methods: {
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
