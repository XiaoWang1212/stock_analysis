<template>
  <div class="stochrsi-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是隨機相對強弱指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <div class="info-box-title">隨機相對強弱指標(STOCHRSI)</div>
      <div class="info-box-content">
        隨機相對強弱指標，結合RSI指標與STOCH指標，利用收盤價計算每日K棒的RSI值，並參考隨機指標計算方式，將RSI指標轉換為隨機相對強弱指標，數值同樣介於0~100之間
      </div>
      <div class="info-box-content">
        依據STOCHRSI可判斷股市買賣情形，當數值超過80即為超買，低於20即為超賣，提醒投資者小心極端的市場買賣情形
      </div>
      <img src="@/assets/photos/STOCHRSI.png" alt="STOCHRSI Photo" />
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
      ...mapActions("stockApp", [
        "fetchSMAChartData",
        "generateTwStockNameMap",
      ]),

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
        const { dates, stochrsi_fastk, stochrsi_fastd } = this.chartData;

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const traceK = {
          x: indices,
          y: stochrsi_fastk,
          type: "scatter",
          mode: "lines",
          name: "K值",
          line: { color: "#FFA042" },
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>K值:</b> %{y:.4f}<br>" +
            "<extra></extra>",
        };

        const traceD = {
          x: indices,
          y: stochrsi_fastd,
          type: "scatter",
          mode: "lines",
          name: "D值",
          line: { color: "#02DF82" },
          hovertemplate: "<br><b>D值:</b> %{y:.4f}<br>" + "<extra></extra>",
        };

        const overboughtArea = {
          x: [indices[0], indices[indices.length - 1]],
          y: [80, 80],
          mode: "lines",
          line: {
            color: "#FF2D2D",
            width: 1,
            dash: "dash",
          },
          name: "超買區",
          hoverinfo: "none",
        };

        const oversoldArea = {
          x: [indices[0], indices[indices.length - 1]],
          y: [20, 20],
          mode: "lines",
          line: {
            color: "#66B3FF",
            width: 1,
            dash: "dash",
          },
          name: "超賣區",
          hoverinfo: "none",
        };

        const overboughtRegion = {
          x: [
            indices[0],
            indices[indices.length - 1],
            indices[indices.length - 1],
            indices[0],
          ],
          y: [80, 80, 100, 100],
          fill: "toself",
          fillcolor: "rgba(255, 200, 200, 0.2)",
          line: { width: 0 },
          name: "超買區域",
          hoverinfo: "none",
          showlegend: false,
        };

        const oversoldRegion = {
          x: [
            indices[0],
            indices[indices.length - 1],
            indices[indices.length - 1],
            indices[0],
          ],
          y: [0, 0, 20, 20],
          fill: "toself",
          fillcolor: "rgba(200, 200, 255, 0.2)",
          line: { width: 0 },
          name: "超賣區域",
          hoverinfo: "none",
          showlegend: false,
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` - ${this.displayName}`;
        }
        chartTitle += ` STOCHRSI Chart`;

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
          annotations: [
            {
              x: indices[0],
              y: 80,
              xref: "x",
              yref: "y",
              text: "超買區",
              showarrow: false,
              font: {
                color: "#FF2D2D",
                size: 10,
              },
              xanchor: "left",
            },
            {
              x: indices[0],
              y: 20,
              xref: "x",
              yref: "y",
              text: "超賣區",
              showarrow: false,
              font: {
                color: "#66B3FF",
                size: 10,
              },
              xanchor: "left",
            },
          ],
          paper_bgcolor: '#4F4F4F',
          plot_bgcolor: '#4F4F4F',
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [
            traceK,
            traceD,
            oversoldRegion, 
            overboughtRegion,
            oversoldArea,
            overboughtArea,
          ],
          layout
        );
      },
    },
    async mounted() {
      if (
        this.market === "TW" &&
        (!this.twStockNameMap || Object.keys(this.twStockNameMap).length === 0)
      ) {
        try {
          await this.generateTwStockNameMap();
        } catch (error) {
          console.error("獲取台股名稱映射時出錯:", error);
        }
      }

      this.fetchChartData();
    },
    beforeUnmount() {
      if (this.$refs.chartContainer) {
        Plotly.purge(this.$refs.chartContainer);
      }
    },
  };
</script>

<style scoped>
  .stochrsi-chart {
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
