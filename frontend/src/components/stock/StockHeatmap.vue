<template>
  <div class="stock-heatmap">
    <h3>股票分類地圖</h3>
    <p v-if="loading" class="loading">Loading chart data...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div
      v-if="stockData.length"
      ref="heatmapContainer"
      class="heatmap-container"
    ></div>

    <!-- 懸浮資訊面板 -->
    <div v-if="hoveredInfo" class="hover-info" :style="chartPosition">
      <div
        v-for="stock in hoveredInfo.stocks"
        :key="stock.ticker"
        class="stock-item"
        :class="{ positive: stock.change > 0, negative: stock.change < 0 }"
      >
        <div class="stock-info">
          <span class="ticker">{{ stock.ticker }}</span>
          <span class="change">{{ stock.change.toFixed(2) }}%</span>
        </div>
        <MiniStockChart v-if="stock.chartData" :chartData="stock.chartData" />
      </div>
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { mapState, mapActions } from "vuex";
  import { nextTick } from "vue";
  import MiniStockChart from "./MiniStockChart.vue";

  export default {
    components: {
      MiniStockChart,
    },
    data() {
      return {
        stockData: [],
        hoveredInfo: null,
        chartPosition: {
          top: "0px",
          left: "0px",
        },
      };
    },
    computed: {
      ...mapState("stockApp", {
        loading: (state) => state.loading,
        error: (state) => state.error,
      }),
    },
    methods: {
      ...mapActions("stockApp", ["fetchStockCategories"]),
      async fetchStockData() {
        this.stockData = [];
        await this.fetchStockCategories();
        if (!this.error) {
          this.stockData = this.$store.state.stockApp.stockData;
          await nextTick(); // 確保 DOM 更新完成
          this.renderHeatmap();
        }
      },
      async renderHeatmap() {
        await nextTick();

        // 篩選符合 S&P 500 標準的股票
        const filteredStockData = this.stockData.filter((item) => {
          return (
            // 市值大於 82 億美元
            item.marketCap >= 8.2e9
          );
        });

        this.stockData = filteredStockData;

        this.stockData.forEach((item) => {
          item.sector =
            item.sector && item.sector !== "N/A" ? item.sector : "Unknown";
          item.industry =
            item.industry && item.industry !== "N/A"
              ? item.industry
              : "Unknown";
          item.marketCap = item.marketCap || 0;
        });

        const sectors = [...new Set(this.stockData.map((item) => item.sector))];
        const industries = [
          ...new Set(this.stockData.map((item) => item.industry)),
        ];

        const sectorLabels = sectors.map((sector) => `${sector}`);
        const industryLabels = industries.map((industry) => `${industry}`);
        const stockLabels = this.stockData.map((item) => `${item.name}`);

        // 建立一個映射來儲存公司名稱對應的股票代碼和變化百分比
        const stockInfoMap = new Map(
          this.stockData.map((item) => [
            item.name,
            { ticker: item.ticker, change: item.change },
          ])
        );

        const data = [
          {
            type: "treemap",
            labels: ["All"]
              .concat(sectorLabels)
              .concat(industryLabels)
              .concat(stockLabels),
            parents: [""]
              .concat(sectors.map(() => "All"))
              .concat(
                industries.map(
                  (industry) =>
                    this.stockData.find((stock) => stock.industry === industry)
                      ?.sector || "Unknown"
                )
              )
              .concat(this.stockData.map((item) => item.industry)),
            values: [0]
              .concat(sectors.map(() => 0))
              .concat(industries.map(() => 0))
              .concat(this.stockData.map((item) => item.marketCap)),
            text: [""] // 為 "All" 添加空文字
              .concat(sectors.map(() => "")) // 為 sectors 添加空文字
              .concat(industries.map(() => "")) // 為 industries 添加空文字
              .concat(
                stockLabels.map((name) => {
                  // 為每個股票添加對應的代碼和變化百分比
                  const info = stockInfoMap.get(name);
                  return info
                    ? `${info.ticker}<br>${info.change.toFixed(2)}%`
                    : "";
                })
              ),
            textinfo: "text",
            textposition: "middle center",
            textfont: {
              size: 14, // 基本字體大小
              family: "Arial",
            },
            insidetextfont: {
              size: [0] // "All" 的字體大小
                .concat(sectors.map(() => 0)) // sectors 的字體大小
                .concat(industries.map(() => 0)) // industries 的字體大小
                .concat(
                  this.stockData.map((item) =>
                    Math.min(24, Math.max(14, Math.sqrt(item.marketCap / 1e8)))
                  )
                ), // 根據市值動態調整字體大小
            },
            marker: {
              colors: ["white"] // 為 "All" 添加顏色
                .concat(sectors.map(() => "white")) // 為 sectors 添加顏色
                .concat(industries.map(() => "white")) // 為 industries 添加顏色
                .concat(
                  stockLabels.map((name) => {
                    // 為每個股票添加對應的變化顏色
                    const info = stockInfoMap.get(name);
                    return info ? info.change : 0;
                  })
                ),
              colorscale: [
                [0, "rgb(255, 0, 0)"],
                [0.5, "rgb(255, 255, 0)"],
                [1, "rgb(0, 255, 0)"],
              ],
              cmin: -3,
              cmax: 3,
              showscale: true,
              colorbar: {
                title: "Change %",
                titleside: "right",
              },
            },
          },
        ];

        const layout = {
          title: "Stock Market Performance",
          margin: { t: 30, l: 0, r: 0, b: 0 },
          height: 1000,
        };

        Plotly.newPlot(this.$refs.heatmapContainer, data, layout);
        // 添加事件監聽器
        this.$refs.heatmapContainer.on("plotly_hover", async (data) => {
          const point = data.points[0];
          let category, stocks;

          // 使用原生事件對象來獲取滑鼠位置
          const event = data.event;

          // 如果是股票層級
          if (point.data.text[point.pointNumber]) {
            const stockInfo = this.stockData.find(
              (item) => item.name === point.label
            );
            if (stockInfo) {
              category = stockInfo.industry;
              // 只獲取相同 industry 的股票數據
              stocks = await Promise.all(
                this.stockData
                  .filter(
                    (item) =>
                      // 確保是同一個產業
                      item.industry === stockInfo.industry &&
                      // 確保是同一個 sector
                      item.sector === stockInfo.sector
                  )
                  .map(async (item) => {
                    const response = await fetch(
                      `/stock_app/api/stock_data/${item.ticker}`
                    );
                    const chartData = await response.json();
                    return {
                      ticker: item.ticker,
                      change: item.change,
                      chartData: chartData,
                    };
                  })
              );
              stocks.sort((a, b) => b.change - a.change);
            }
          }
          // 如果是產業層級
          else if (point.parent === "All") {
            category = point.label;
            // 找出該產業的所有股票
            stocks = this.stockData
              .filter((item) => item.sector === point.label)
              .map((item) => ({
                ticker: item.ticker,
                change: item.change,
              }))
              .sort((a, b) => b.change - a.change);
          }

          if (stocks && stocks.length > 0) {
            this.hoveredInfo = {
              category,
              stocks,
            };

            this.chartPosition = {
              top: `${event.pageY}px`, // 使用 pageY 而不是 clientY
              left: `${event.pageX}px`, // 使用 pageX 而不是 clientX
            };
          }
        });

        this.$refs.heatmapContainer.on("plotly_unhover", () => {
          this.hoveredInfo = null;
        });
      },
    },
    mounted() {
      this.fetchStockData();
    },
  };
</script>

<style scoped>
  .stock-heatmap {
    margin-top: 20px;
    position: relative;
  }

  .heatmap-container {
    height: 600px;
  }

  .loading {
    color: #007bff;
  }

  .error {
    color: #ff0000;
  }

  .floating-chart {
    position: fixed;
    z-index: 1000;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 400px;
  }

  .hover-info {
    position: fixed; /* 確保使用固定定位 */
    z-index: 1000;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    min-width: 300px;
    transform: translate(20px, 20px); /* 添加偏移量 */
  }

  .info-header {
    font-weight: bold;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
    margin-bottom: 8px;
  }

  .stocks-list {
    max-height: 300px;
    overflow-y: auto;
  }

  .stock-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
  }

  .stock-info {
    display: flex;
    flex-direction: column;
    min-width: 100px;
  }

  .positive {
    color: #00c805;
  }

  .negative {
    color: #ff333a;
  }

  .ticker {
    font-weight: bold;
  }

  .change {
    margin-left: 10px;
  }
</style>
