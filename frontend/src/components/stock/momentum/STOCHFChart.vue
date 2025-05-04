<template>
  <div class="stochf-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是隨機快速指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <div class="info-box-title">隨機快速指標(STOCHF)</div>
      <div class="info-box-content">
        隨機快速指標，從隨機指標延伸而來，與隨機指標差別在於，隨機快速指標以RSV值計算公式取代隨機指標的K值計算方式，減少一次的平滑運算，因此對於短期股市趨勢反應較為敏感
      </div>
      <div class="info-box-content"> 
        STOCHF常用的觀察方式為，下降的K線穿越超買區域的D線時，即產生賣出信號；上升的K線穿越超賣區域的D線時，即產生買入信號
      </div>
      <img src="@/assets/photos/STOCHF.png" alt="STOCHF Photo" />
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
        const { dates, stochf_fastk, stochf_fastd } = this.chartData;

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const traceK = {
          x: indices,
          y: stochf_fastk,
          type: "scatter",
          mode: "lines",
          name: "K值",
          line: { color: "#FF79BC" },
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>K值:</b> %{y:.4f}<br>" +
            "<extra></extra>",
        };

        const traceD = {
          x: indices,
          y: stochf_fastd,
          type: "scatter",
          mode: "lines",
          name: "D值",
          line: { color: "#66B3FF" },
          hovertemplate:
            "<br><b>MACD:</b> %{y:.4f}<br>"+
            "<extra></extra>",
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` - ${this.displayName}`;
        }
        chartTitle += ` STOCHF Chart`;

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
          showlegend: true,
          hovermode: "x unified",
          hoverlabel: {
            bgcolor: "#6C6C6C",
            bordercolor: "#BEBEBE",
            font: { size: 12, color: "#BEBEBE"},
          },
          paper_bgcolor: '#4F4F4F',
          plot_bgcolor: '#4F4F4F',
        };

        Plotly.newPlot(this.$refs.chartContainer, [traceK, traceD], layout);
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
    beforeUnmount(){
      if (this.$refs.chartContainer) {
        Plotly.purge(this.$refs.chartContainer);
      }
    }
  };
</script>

<style scoped>
  .stochf-chart {
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
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    top: 40px;
    right: 10px;
    width: 300px;
    z-index: 1000;
  }

  .info-box-title{
    margin-bottom: 5px;
    font-size: 16px;
    font-weight: bold;
    color: #333;
  }

  .info-box-content {
    margin-bottom: 5px;
    font-size: 14px;
    color: #333;
  }

  .info-box img {
    max-width: 100%;
    height: auto;
  }
</style>
