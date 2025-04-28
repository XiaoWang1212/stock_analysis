<template>
  <div class="stoch-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是隨機指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>隨機指標(STOCH)</p>
      <p>
        又稱為KD指標，顧名思義是由K值與D值組合而成。K值為快速平均值，對股市近期變化較為敏感；D值為慢速平均值，對股市近期變化較為遲緩，因此投資人多利用KD指標的相對位置作為進出場時機的判斷輔助
      </p>
      <p>
        根據繪製出的圖表，可觀察K值（橘線）與D值（綠線）的交叉時機，判斷進出場時機，除此之外，也可透過KD值觀察市場上超買或超賣的情形，捕捉價格修正的情形
      </p>
      <img src="@/assets/photos/STOCH.png" alt="STOCH Photo" />
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
        const { dates, slowk, slowd } = this.chartData;

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const traceK = {
          x: indices,
          y: slowk,
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
          y: slowd,
          type: "scatter",
          mode: "lines",
          name: "D值",
          line: { color: "#02DF82" },
          hovertemplate: "<br><b>MACD:</b> %{y:.4f}<br>" + "<extra></extra>",
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
        chartTitle += ` STOCH Chart`;

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
  .stoch-chart {
    border-radius: 8px;
    border-top: 2px solid #7B7B7B;
    background-color: #4F4F4F;
  }

  .chart-container {
    position: relative;
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }

  .info-container {
    cursor: pointer;
    display: flex;
    align-items: center;
    position: absolute;
    top: 10px;
    right: 160px;
  }

  .info-icon {
    font-size: 24px;
    margin-right: 5px;
  }

  .info-text {
    font-size: 14px;
    color: #007bff;
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
