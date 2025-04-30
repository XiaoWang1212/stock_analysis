<template>
  <div class="rsi-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是相對強弱指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>相對強弱指標(RSI)</p>
      <p>
        由股價的平均上漲、下跌幅度計算而得，代表股價的上漲力道強弱，數值介於0~100之間，數值越大代表上漲力道越強。
      </p>
      <img src="@/assets/photos/RSI.png" alt="RSI Photo" />
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { mapState, mapActions } from "vuex";
  import { nextTick } from "vue";

  export default {
    props: {
      symbol: {
        type: String,
        required: true,
      },
      market: {
        type: String,
        required: true,
      },
      stockName: {
        type: String,
        default: "",
      },
    },
    data() {
      return {
        chartData: null,
        showInfo: false,
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        error: (state) => state.error,
        twStockNameMap: (state) => state.twStockNameMap,
      }),

      displayName() {
        // 如果已經從父組件接收了名稱，則使用它
        if (this.stockName) {
          return this.stockName;
        }

        // 如果是台股
        if (this.market === "TW" && this.twStockNameMap) {
          return this.twStockNameMap[this.symbol] || "";
        }

        return ""; // 預設空字串
      },
    },
    watch: {
      symbol: "fetchChartData",
      market: "fetchChartData",
    },
    methods: {
      ...mapActions("stockApp", ["fetchSMAChartData", "generateTwStockNameMap"]),

      async fetchChartData() {
        this.chartData = null;

        if (
          this.market === "TW" &&
          (!this.twStockNameMap ||
            Object.keys(this.twStockNameMap).length === 0)
        ) {
          await this.generateTwStockNameMap();
        }

        await this.fetchSMAChartData(this.symbol, this.market);
        if (!this.error) {
          this.chartData = this.$store.state.stockApp.chartData;
          await nextTick(); // 確保 DOM 更新完成
          this.renderChart();
        }
      },
      async renderChart() {
        await nextTick(); // 確保 DOM 更新完成
        const { dates, rsi_6, rsi_24 } = this.chartData;

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const traceRSI6 = {
          x: indices,
          y: rsi_6,
          type: "scatter",
          mode: "lines",
          name: "RSI 6",
          line: { color: "#FF79BC" },
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>RSI 6:</b> %{y:.4f}<br>" +
            "<extra></extra>",
        };

        const traceRSI24 = {
          x: indices,
          y: rsi_24,
          type: "scatter",
          mode: "lines",
          name: "RSI 24",
          line: { color: "#66B3FF" },
          hovertemplate:
            "<br><b>RSI 24:</b> %{y:.4f}<br>"+
            "<extra></extra>",
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` - ${this.displayName}`;
        }
        chartTitle += ` RSI Chart`;

        const layout = {
          title: {
            text: chartTitle,
            font: {
              color: 'white',
            }
          },
          legend: {
            font: {
              color: "#BEBEBE"
            },
          },
          xaxis: { title: "Date", color: '#BEBEBE', gridcolor: '#7B7B7B'},
          yaxis: { title: "RSI", color: '#BEBEBE', gridcolor: '#7B7B7B'},
          showlegend: true,
          hovermode: "x unified",
          paper_bgcolor: '#4F4F4F',
          plot_bgcolor: '#4F4F4F',
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [traceRSI6, traceRSI24],
          layout
        );
      },
    },
    async mounted() {
      if (this.market === "TW" && (!this.twStockNameMap || Object.keys(this.twStockNameMap).length === 0)) {
        try {
          await this.generateTwStockNameMap();
        } catch (error) {
          console.error("獲取台股名稱映射時出錯:", error);
        }
      }
      
      this.fetchChartData();
    },
  };
</script>

<style scoped>
  .rsi-chart {
    border-radius: 8px;
    border-top: 2px solid #7B7B7B;
    background-color: #4F4F4F;
    position: relative;
  }

  .chart-container {
    
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }

  .info-container {
    position: absolute;
    right: 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
  }

  .info-icon {
    font-size: 24px;
    margin-right: 5px;
    color: #66B3FF;
  }

  .info-text {
    font-size: 14px;
    color: white;
  }

  .info-box {
    background-color: #f9f9f9;
    border: 1px solid #ccc;
    padding: 10px;
    position: absolute;
    top: 40px;
    right: 10px;
    width: 300px;
    z-index: 1000;
  }

  .info-box img {
    max-width: 100%;
    height: auto;
  }
</style>
