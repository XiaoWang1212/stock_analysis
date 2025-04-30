<template>
  <div class="macd-chart">
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="chartData" ref="chartContainer" class="chart-container"></div>
    <div class="info-container" @click="showInfo = !showInfo">
      <span class="material-icons info-icon">info</span>
      <span class="info-text">什麼是平滑異同移動平均線指標?</span>
    </div>
    <div v-if="showInfo" class="info-box">
      <p>平滑異同移動平均線指標(MACD)</p>
      <p>
        MACD指標是透過DIF線與MACD線的交叉，來判斷買入與賣出的訊號。除此之外，若股價創新低，但MACD線卻出現上升的情形，常被認為是買入訊號，即為多頭背離，相反，若股價創新高，但MACD線卻出現下降的情形，常被認為是賣出訊號，即為空頭背離
      </p>
      <img src="@/assets/photos/MACD.png" alt="MACD Photo" />
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
        const {
          dates,
          macd,
          macd_signal,
          close_prices,
          high_prices,
          low_prices,
          open_prices,
          sma_5,
          sma_20,
          sma_60,
        } = this.chartData;

        const indices = Array.from({ length: dates.length }, (_, i) => i);

        const traceCandlestick = {
          x: indices,
          close: close_prices,
          high: high_prices,
          low: low_prices,
          open: open_prices,
          type: "candlestick",
          name: "K線圖",
          xaxis: "x",
          yaxis: "y",
          increasing: { line: { color: "#FF2D2D" }, fillcolor: "#FFCCCC" },
          decreasing: { line: { color: "#02DF82" }, fillcolor: "#CCFFCC" },
          text: dates,
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>開盤:</b> %{open:.2f}<br>" +
            "<b>最高:</b> %{high:.2f}<br>" +
            "<b>最低:</b> %{low:.2f}<br>" +
            "<b>收盤:</b> %{close:.2f}<br>" +
            "<extra></extra>",
        };

        const traceSMA5 = {
          x: indices,
          y: sma_5,
          type: "scatter",
          mode: "lines",
          name: "SMA 5",
          xaxis: "x",
          yaxis: "y",
          line: { color: "#FF79BC", width: 1.5 },
          text: dates,
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>SMA 5:</b> %{y:.2f}<br>" +
            "<extra></extra>",
        };

        const traceSMA20 = {
          x: indices,
          y: sma_20,
          type: "scatter",
          mode: "lines",
          name: "SMA 20",
          xaxis: "x",
          yaxis: "y",
          line: { color: "#66B3FF", width: 1.5 },
          text: dates,
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>SMA 20:</b> %{y:.2f}<br>" +
            "<extra></extra>",
        };

        const traceSMA60 = {
          x: indices,
          y: sma_60,
          type: "scatter",
          mode: "lines",
          name: "SMA 60",
          xaxis: "x",
          yaxis: "y",
          line: { color: "#9F35FF", width: 1.5 },
          text: dates,
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>SMA 60:</b> %{y:.2f}<br>" +
            "<extra></extra>",
        };

        // 識別價格最高點和最低點 (僅考慮可視範圍的數據)
        const highPoints = [];
        const lowPoints = [];

        // 這個窗口大小決定了我們尋找局部最高/最低點的範圍
        const window = 10;

        for (let i = window; i < close_prices.length - window; i++) {
          let isHighest = true;
          let isLowest = true;

          // 檢查周圍窗口內是否為最高點或最低點
          for (let j = i - window; j <= i + window; j++) {
            if (j !== i) {
              if (high_prices[j] >= high_prices[i]) isHighest = false;
              if (low_prices[j] <= low_prices[i]) isLowest = false;
            }
          }

          if (isHighest) {
            highPoints.push({
              x: indices[i],
              y: high_prices[i],
              date: dates[i],
            });
          }

          if (isLowest) {
            lowPoints.push({
              x: indices[i],
              y: low_prices[i],
              date: dates[i],
            });
          }
        }

        const traceHighPoints = {
          x: highPoints.map((point) => point.x),
          y: highPoints.map((point) => point.y),
          type: "scatter",
          mode: "markers",
          marker: {
            symbol: "circle",
            size: 8,
            color: "#FF2D2D",
            line: { width: 1, color: "white" },
          },
          name: "價格高點",
          xaxis: "x",
          yaxis: "y",
          text: highPoints.map((point) => `高點: ${point.y.toFixed(2)}`),
          customdata: highPoints.map((point) => point.date),
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>%{text}</b><br>" +
            "<extra></extra>",
        };

        const traceLowPoints = {
          x: lowPoints.map((point) => point.x),
          y: lowPoints.map((point) => point.y),
          type: "scatter",
          mode: "markers",
          marker: {
            symbol: "circle",
            size: 8,
            color: "#02DF82",
            line: { width: 1, color: "white" },
          },
          name: "價格低點",
          xaxis: "x",
          yaxis: "y",
          text: lowPoints.map((point) => `低點: ${point.y.toFixed(2)}`),
          customdata: lowPoints.map((point) => point.date),
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>%{text}</b><br>" +
            "<extra></extra>",
        };

        // 計算直方圖數據 (DIF - MACD信號線的差值)
        const histogram = [];
        const histogramColors = [];

        for (let i = 0; i < macd.length; i++) {
          // 確保數據有效
          if (macd[i] !== null && macd_signal[i] !== null) {
            const value = macd[i] - macd_signal[i];
            histogram.push(value);
            // 使用紅綠對比色：正值為紅色，負值為綠色 (符合大多數台灣投資者的習慣)
            histogramColors.push(value >= 0 ? "#FF2D2D" : "#02DF82");
          } else {
            histogram.push(null);
            histogramColors.push("#9D9D9D"); // 缺失數據用灰色
          }
        }

        const traceHistogram = {
          x: indices,
          y: histogram,
          type: "bar",
          name: "柱狀圖",
          xaxis: "x2",
          yaxis: "y2",
          marker: {
            color: 	histogramColors,
          },
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>柱狀值:</b> %{y:.4f}<br>" +
            "<extra></extra>",
        };

        const traceDIF = {
          x: indices,
          y: macd,
          type: "scatter",
          mode: "lines",
          name: "DIF",
          xaxis: "x2",
          yaxis: "y2",
          line: { color: "#FF79BC", width: 2 },
          customdata: dates,
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>DIF:</b> %{y:.4f}<br>" +
            "<extra></extra>",
        };

        const traceMACD = {
          x: indices,
          y: macd_signal,
          type: "scatter",
          mode: "lines",
          name: "MACD",
          xaxis: "x2",
          yaxis: "y2",
          line: { color: "#66B3FF", width: 2 },
          hovertemplate: "<br><b>MACD:</b> %{y:.4f}<br>" + "<extra></extra>",
        };

        const buySellSignals = [];

        for (let i = 1; i < macd.length; i++) {
          // 確保數據有效
          if (
            macd[i] === null ||
            macd_signal[i] === null ||
            macd[i - 1] === null ||
            macd_signal[i - 1] === null
          ) {
            continue;
          }

          // 金叉：DIF從下方穿過MACD信號線
          if (macd[i - 1] < macd_signal[i - 1] && macd[i] > macd_signal[i]) {
            buySellSignals.push({
              x: indices[i],
              y: macd[i],
              date: dates[i],
              text: "買入訊號 (金叉)",
              color: "#02DF82",
              symbol: "triangle-up",
            });
          }

          // 死叉：DIF從上方穿過MACD信號線
          if (macd[i - 1] > macd_signal[i - 1] && macd[i] < macd_signal[i]) {
            buySellSignals.push({
              x: indices[i],
              y: macd[i],
              date: dates[i],
              text: "賣出訊號 (死叉)",
              color: "#FF2D2D",
              symbol: "triangle-down",
            });
          }
        }

        // 金叉死叉訊號
        const traceSignals = {
          x: buySellSignals.map((signal) => signal.x),
          y: buySellSignals.map((signal) => signal.y),
          type: "scatter",
          mode: "markers",
          xaxis: "x2",
          yaxis: "y2",
          marker: {
            symbol: buySellSignals.map((signal) => signal.symbol),
            size: 10,
            color: buySellSignals.map((signal) => signal.color),
            line: { width: 1, color: "white" },
          },
          name: "交叉訊號",
          text: buySellSignals.map((signal) => signal.text),
          customdata: buySellSignals.map((signal) => signal.date),
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>%{text}</b><br>" +
            "<b>DIF值:</b> %{y:.4f}<br>" +
            "<extra></extra>",
        };

        // 添加零線
        const traceZeroLine = {
          x: [indices[0], indices[indices.length - 1]],
          y: [0, 0],
          type: "scatter",
          mode: "lines",
          xaxis: "x2",
          yaxis: "y2",
          line: {
            color: "#ADADAD",
            width: 1,
            dash: "dash",
          },
          name: "零線",
          hoverinfo: "none",
          showlegend: false,
        };

        // 檢查背離
        const divergences = [];
        const recentHighs = [];
        const recentLows = [];

        // 收集高點和低點用於背離分析
        for (let i = window; i < close_prices.length - window; i++) {
          if (i < 30) continue; // 跳過前面的日子，避免錯誤的背離識別

          // 判斷價格高點
          let isPriceHigh = true;
          for (let j = i - 5; j <= i + 5; j++) {
            if (j !== i && j >= 0 && j < close_prices.length) {
              if (high_prices[j] > high_prices[i]) {
                isPriceHigh = false;
                break;
              }
            }
          }

          // 判斷價格低點
          let isPriceLow = true;
          for (let j = i - 5; j <= i + 5; j++) {
            if (j !== i && j >= 0 && j < close_prices.length) {
              if (low_prices[j] < low_prices[i]) {
                isPriceLow = false;
                break;
              }
            }
          }

          // 收集高點
          if (isPriceHigh) {
            recentHighs.push({
              index: i,
              price: high_prices[i],
              macd: macd[i],
            });

            // 只保留最近的高點
            if (recentHighs.length > 5) {
              recentHighs.shift();
            }
          }

          // 收集低點
          if (isPriceLow) {
            recentLows.push({
              index: i,
              price: low_prices[i],
              macd: macd[i],
            });

            // 只保留最近的低點
            if (recentLows.length > 5) {
              recentLows.shift();
            }
          }

          // 檢查頂背離：價格創新高但 MACD 未創新高
          if (recentHighs.length >= 2) {
            const last = recentHighs[recentHighs.length - 1];
            const prev = recentHighs[recentHighs.length - 2];

            if (last.price > prev.price && last.macd < prev.macd) {
              divergences.push({
                x: indices[last.index],
                y: high_prices[last.index],
                type: "bearish", // 空頭背離
                date: dates[last.index],
              });
            }
          }

          // 檢查底背離：價格創新低但 MACD 未創新低
          if (recentLows.length >= 2) {
            const last = recentLows[recentLows.length - 1];
            const prev = recentLows[recentLows.length - 2];

            if (last.price < prev.price && last.macd > prev.macd) {
              divergences.push({
                x: indices[last.index],
                y: low_prices[last.index],
                type: "bullish", // 多頭背離
                date: dates[last.index],
              });
            }
          }
        }

        // 繪製背離點
        const traceDivergence = {
          x: divergences.map((div) => div.x),
          y: divergences.map((div) => div.y),
          type: "scatter",
          mode: "markers",
          marker: {
            symbol: divergences.map((div) =>
              div.type === "bullish" ? "star-triangle-up" : "star-triangle-down"
            ),
            size: 12,
            color: divergences.map((div) =>
              div.type === "bullish" ? "#00FF00" : "#FF00FF"
            ),
            line: { width: 1, color: "white" },
          },
          name: "背離",
          xaxis: "x",
          yaxis: "y",
          text: divergences.map(
            (div) => `${div.type === "bullish" ? "多頭背離" : "空頭背離"}`
          ),
          customdata: divergences.map((div) => div.date),
          hovertemplate:
            "<b>%{customdata}</b><br>" +
            "<b>%{text}</b><br>" +
            "<extra></extra>",
        };

        let chartTitle = `${this.symbol}`;
        if (this.market === "TW" && this.displayName) {
          chartTitle += ` (${this.displayName})`;
        }
        chartTitle += ` MACD Chart`;

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
          grid: {
            rows: 2,
            columns: 1,
            pattern: "independent",
            roworder: "top to bottom",
          },
          xaxis: { title: "Date", rangeslider: { visible: false }, color: '#BEBEBE', gridcolor: '#7B7B7B'},
          yaxis: {
            title: "Price",
            autorange: true,
            color: '#BEBEBE', 
            gridcolor: '#7B7B7B',
          },
          xaxis2: { title: "Date", rangeslider: { visible: false }, color: '#BEBEBE', gridcolor: '#7B7B7B'},
          yaxis2: {
            title: "MACD 值",
            showgrid: false,
            color: '#BEBEBE', 
            gridcolor: '#7B7B7B'
          },
          showlegend: true,
          hovermode: "x unified",
          annotations: [
            {
              x: indices[indices.length - 1],
              y: 0,
              xref: "x2",
              yref: "y2",
              text: "零線",
              showarrow: false,
              font: {
                color: "gray",
                size: 10,
              },
              xanchor: "right",
              yanchor: "bottom",
            },
          ],
          paper_bgcolor: '#4F4F4F',
          plot_bgcolor: '#4F4F4F',
        };

        Plotly.newPlot(
          this.$refs.chartContainer,
          [
            //上半
            traceCandlestick,
            traceSMA5,
            traceSMA20,
            traceSMA60,
            traceHighPoints,
            traceLowPoints,
            traceDivergence,

            //下半
            traceHistogram,
            traceZeroLine,
            traceDIF,
            traceMACD,
            traceSignals,
          ],
          layout,
          {
            responsive: true,
            displaylogo: false,
            modeBarButtonsToRemove: ["lasso2d", "select2d"],
            toImageButtonOptions: {
              format: "png",
              filename: `${this.symbol}_combined_chart`,
            },
          }
        );
      },
    },
    mounted() {
      this.fetchChartData();
    },
  };
</script>

<style scoped>
  .macd-chart {
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

  .info-box p {
    margin: 0;
    font-size: 14px;
    color: #333;
  }

  .info-box img {
    max-width: 100%;
    height: auto;
  }
</style>
