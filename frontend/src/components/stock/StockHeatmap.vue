<template>
  <div class="stock-heatmap">
    <!-- Loading Spinner 移到最外層 -->
    <div v-if="isLoading" class="loading-overlay">
      <loading-spinner />
    </div>

    <div class="header-controls">
      <h3>S&P 500</h3>
      <button v-if="show404Error" @click="handleReload" class="reload-button">
        重新載入資料
      </button>
    </div>
    <div
      v-if="stockData.length"
      ref="heatmapContainer"
      class="heatmap-container"
    >
      <error-message
        v-if="error"
        :message="error"
        retryable
        @retry="fetchStockCategories"
      />
    </div>

    <!-- 懸浮資訊面板 -->
    <div
      v-if="hoveredInfo"
      class="hover-info"
      :style="{ top: chartPosition.top, left: chartPosition.left }"
    >
      <!-- 當前滑鼠指到的股票 -->
      <div
        v-if="hoveredInfo.currentStock"
        class="current-stock"
        :class="{
          'positive-bg': hoveredInfo.currentStock.change > 0,
          'negative-bg': hoveredInfo.currentStock.change < 0,
        }"
      >
        <div class="stock-info">
          <span class="ticker">{{ hoveredInfo.currentStock.ticker }}</span>
          <span class="price">${{ hoveredInfo.currentStock.price }}</span>
          <span class="change"
            >{{ hoveredInfo.currentStock.change.toFixed(2) }}%</span
          >
        </div>
        <MiniStockChart
          v-if="hoveredInfo.currentStock.chartData"
          :chartData="hoveredInfo.currentStock.chartData"
        />
      </div>

      <!-- 同產業其他股票列表 -->
      <div class="stocks-list">
        <div
          v-for="stock in sortedStocks"
          :key="stock.ticker"
          class="stock-item"
          :class="{
            positive: stock.change > 0,
            negative: stock.change < 0,
            current: stock.ticker === hoveredInfo.currentStock?.ticker,
          }"
        >
          <div class="stock-info">
            <span class="ticker">{{ stock.ticker }}</span>
            <span class="price">${{ stock.price }}</span>
            <span class="change">{{ stock.change.toFixed(2) }}%</span>
          </div>
          <MiniStockChart v-if="stock.chartData" :chartData="stock.chartData" />
        </div>
      </div>
    </div>
    <button @click="handleReload" class="reload-button">重新載入</button>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { mapState, mapActions } from "vuex";
  import { nextTick } from "vue";
  import MiniStockChart from "./MiniStockChart.vue";
  import LoadingSpinner from "../common/LoadingSpinner.vue";
  import ErrorMessage from "../common/ErrorMessage.vue";
  import { CACHE_KEYS, cacheManager } from "@/services/cacheManager.js";

  export default {
    components: {
      MiniStockChart,
      LoadingSpinner,
      ErrorMessage,
    },
    data() {
      return {
        stockData: [],
        failedStocks: new Set(), // 追蹤失敗的股票
        hoveredInfo: null,
        chartPosition: {
          top: "0px",
          left: "0px",
        },
        stockChartDataMap: new Map(),
        preloadedData: null, // 用於存儲預加載的數據
        cachedData: null,
        cacheExpiry: null,
        CACHE_DURATION: 24 * 60 * 60 * 1000, // 改為一天的毫秒數
        apiRequestsCompleted: 0,
        totalApiRequests: 0,
        show404Error: false,
        showReloadButton: false,
        isLocalLoading: false, // 本地 loading 狀態
        dataReady: false, // 本地 ready 狀態
      };
    },
    computed: {
      ...mapState("stockApp", {
        storeLoading: (state) => state.loading, // 重命名避免衝突
        error: (state) => state.error,
      }),
      sortedStocks() {
        if (!this.hoveredInfo) return [];
        return [...this.hoveredInfo.stocks].sort(
          (a, b) => b.marketCap - a.marketCap
        );
      },
      isLoading() {
        return (
          this.storeLoading ||
          this.isLocalLoading ||
          (this.totalApiRequests > 0 &&
            this.apiRequestsCompleted < this.totalApiRequests)
        );
      },
    },
    methods: {
      ...mapActions("stockApp", ["fetchStockCategories"]),
      async handleReload() {
        if (this.failedStocks.size === 0) {
          return;
        }

        try {
          this.isLocalLoading = true;
          const failedStocksArray = Array.from(this.failedStocks);

          for (let i = 0; i < failedStocksArray.length; i++) {
            const ticker = failedStocksArray[i];
            try {
              const response = await fetch(
                `/stock_app/api/stock_data/${ticker}`
              );

              if (response.ok) {
                const data = await response.json();
                // 更新 Map
                this.stockChartDataMap.set(ticker, data);
                // 更新快取
                const cacheKey = `${CACHE_KEYS.STOCK_DATA}${ticker}`;
                cacheManager.setCache(cacheKey, data);
                // 從失敗列表中移除
                this.failedStocks.delete(ticker);
              }
            } catch (error) {
              console.error(`Error reloading ${ticker}:`, error);
            }
          }

          if (this.failedStocks.size === 0) {
            this.showReloadButton = false;
          }

          // 重新渲染圖表
          await this.renderHeatmap();
        } finally {
          this.isLocalLoading = false;
        }
      },
      clearCache() {
        localStorage.removeItem("stockHeatmapCache");
        this.cachedData = null;
        this.cacheExpiry = null;
        this.stockChartDataMap.clear();
      },
      checkCacheExpiry(timestamp) {
        // 取得快取時間和當前時間的日期部分
        const cacheDate = new Date(timestamp).setHours(0, 0, 0, 0);
        const today = new Date().setHours(0, 0, 0, 0);

        // 如果不是同一天，則快取過期
        return cacheDate < today;
      },
      useCache() {
        if (!this.cachedData || !Array.isArray(this.cachedData.stockData)) {
          console.warn("Invalid cache data");
          this.stockData = [];
          return false;
        }

        // 檢查是否為同一天
        if (this.checkCacheExpiry(this.cachedData.timestamp)) {
          console.log("Cache expired - new day");
          return false;
        }

        this.stockData = this.cachedData.stockData;
        this.stockChartDataMap = new Map(this.cachedData.chartData || []);
        this.dataReady = true;
        this.renderHeatmap();
        return true;
      },
      updateCache() {
        this.cachedData = {
          stockData: this.stockData,
          chartData: Array.from(this.stockChartDataMap.entries()),
          timestamp: Date.now(),
        };

        try {
          localStorage.setItem(
            "stockHeatmapCache",
            JSON.stringify({
              timestamp: Date.now(),
              data: this.cachedData,
            })
          );
        } catch (e) {
          console.warn("Failed to save cache to localStorage:", e);
        }
      },
      async preloadAllData() {
        this.isLocalLoading = true;
        try {
          // 檢查是否有快取數據
          const savedCache = localStorage.getItem(CACHE_KEYS.STOCK_HEATMAP);
          if (savedCache) {
            const { timestamp, data } = JSON.parse(savedCache);
            // 如果是同一天，使用快取
            if (!this.checkCacheExpiry(timestamp)) {
              this.cachedData = data;
              if (this.useCache()) {
                return;
              }
            }
          }

          this.loading = true;
          try {
            // 1. 先獲取股票列表
            await this.fetchStockCategories();

            const stocks = this.$store.state.stockApp.stockData.filter(
              (item) => item.marketCap >= 8.2e9
            );

            this.totalApiRequests = stocks.length;
            this.apiRequestsCompleted = 0;

            // 批次處理 API 請求
            const batchSize = 10;
            for (let i = 0; i < stocks.length; i += batchSize) {
              const batch = stocks.slice(i, i + batchSize);
              await Promise.all(
                batch.map(async (stock) => {
                  try {
                    const response = await fetch(
                      `/stock_app/api/stock_data/${stock.ticker}`
                    );
                    if (response.status === 429) {
                      this.failedStocks.add(stock.ticker);
                      this.showReloadButton = true;
                    } else {
                      const data = await response.json();
                      this.stockChartDataMap.set(stock.ticker, data);
                    }
                  } catch (error) {
                    this.failedStocks.add(stock.ticker);
                    this.showReloadButton = true;
                    console.error(
                      `Error fetching data for ${stock.ticker}:`,
                      error
                    );
                  } finally {
                    this.apiRequestsCompleted++;
                    this.showReloadButton = true;
                  }
                })
              );
            }

            // 確保所有數據都準備好了
            this.dataReady = true; // 使用 data 屬性
            this.stockData = stocks;

            // 更新快取
            this.updateCache();

            // 所有數據準備好後再渲染
            await this.renderHeatmap();
          } catch (error) {
            console.error("Error preloading data:", error);
            this.error = "Failed to load stock data";
          } finally {
            this.loading = false;
          }
        } catch (error) {
          console.error("Error loading data:", error);
          this.error = error.message;
        } finally {
          this.isLocalLoading = false;
        }
      },

      calculatePosition(event) {
        const margin = 10; // 邊距

        // 獲取視窗的滾動偏移量
        const scrollLeft =
          window.scrollX || document.documentElement.scrollLeft;
        const scrollTop = window.scrollY || document.documentElement.scrollTop;

        // 計算面板的左邊界和上邊界
        let left = event.clientX + scrollLeft + margin;
        let top = event.clientY + scrollTop + margin;

        // 獲取 hover-info 的尺寸
        const hoverInfo = document.querySelector(".hover-info");
        if (!hoverInfo) return { top: `${top}px`, left: `${left}px` };

        const hoverWidth = hoverInfo.offsetWidth;
        const hoverHeight = hoverInfo.offsetHeight;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // 調整位置避免面板超出視窗
        if (left + hoverWidth > windowWidth + scrollLeft) {
          left = event.clientX + scrollLeft - hoverWidth - margin;
        }
        if (top + hoverHeight > windowHeight + scrollTop) {
          top = event.clientY + scrollTop - hoverHeight - margin;
        }

        return {
          top: `${top}px`,
          left: `${left}px`,
        };
      },
      async renderHeatmap() {
        await nextTick();

        // 確保資料已準備好
        if (!this.dataReady || !this.$refs.heatmapContainer) {
          console.warn("Data or container not ready");
          this.clearCache();
          return;
        }

        try {
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

          const sectors = [
            ...new Set(this.stockData.map((item) => item.sector)),
          ];
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
              hoverinfo: "none",
              labels: ["All"]
                .concat(sectorLabels)
                .concat(industryLabels)
                .concat(stockLabels),
              parents: [""]
                .concat(sectors.map(() => "All"))
                .concat(
                  industries.map(
                    (industry) =>
                      this.stockData.find(
                        (stock) => stock.industry === industry
                      )?.sector || "Unknown"
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
                color: "white",
              },
              insidetextfont: {
                size: [0] // "All" 的字體大小
                  .concat(sectors.map(() => 0)) // sectors 的字體大小
                  .concat(industries.map(() => 0)) // industries 的字體大小
                  .concat(
                    this.stockData.map((item) =>
                      Math.min(
                        24,
                        Math.max(14, Math.sqrt(item.marketCap / 1e8))
                      )
                    )
                  ), // 根據市值動態調整字體大小
              },
              marker: {
                colors: ["black"] // 為 "All" 添加顏色
                  .concat(sectors.map(() => "black")) // 為 sectors 添加顏色
                  .concat(industries.map(() => "black")) // 為 industries 添加顏色
                  .concat(
                    stockLabels.map((name) => {
                      // 為每個股票添加對應的變化顏色
                      const info = stockInfoMap.get(name);
                      return info ? info.change : 0;
                    })
                  ),
                colorscale: [
                  [0, "rgb(255, 0, 0)"],
                  [0.5, "rgb(0, 0, 0)"],
                  [1, "rgb(0, 255, 0)"],
                ],
                cmin: -3,
                cmax: 3,
                showscale: true,
                colorbar: {
                  title: "Change %",
                  titleside: "right",
                },
                line: {
                  color: "rgba(255, 255, 255, 0.7)",
                },
              },
            },
          ];

          const layout = {
            title: "Stock Market Performance",
            margin: { t: 30, l: 0, r: 0, b: 0 },
            height: 600,
            font: {
              color: "#ffffff",
            },
            plot_bgcolor: "rgba(0,0,0,0)",
            paper_bgcolor: "rgba(0,0,0,0)",
            colorbar: {
              tickfont: {
                color: "#ffffff",
              },
              title: {
                text: "Change %",
                font: {
                  color: "#ffffff",
                },
              },
            },
          };

          Plotly.newPlot(this.$refs.heatmapContainer, data, layout);
          this.setupEventListeners();
        } catch (error) {
          console.error("Error rendering heatmap:", error);
        }
      },

      setupEventListeners() {
        const container = this.$refs.heatmapContainer;
        if (!container || !this.dataReady) return;

        try {
          // 移除舊的事件監聽器
          container.removeAllListeners();

          // 重新添加事件監聽器
          container.on("plotly_hover", (data) => {
            if (!this.dataReady) return;
            const point = data.points[0];
            if (!point || !point.data.text[point.pointNumber]) return;

            // 檢查是否為股票項目（通過檢查是否有 text 內容）
            const isStockItem =
              point.data.text[point.pointNumber].includes("<br>");

            if (!isStockItem) {
              this.hoveredInfo = null;
              return;
            }

            const stockInfo = this.stockData.find(
              (item) => item.name === point.label
            );
            if (!stockInfo) return;

            const colors = new Array(point.data.labels.length).fill(
              "rgba(255, 255, 255, 0.3)"
            );
            const widths = new Array(point.data.labels.length).fill(1);

            // 凸顯目標
            colors[point.pointNumber] = "rgba(255, 255, 0, 0.8)";
            widths[point.pointNumber] = 2;

            Plotly.restyle(container, {
              "marker.line": [
                {
                  color: colors,
                  width: widths,
                },
              ],
            });

            const currentStock = {
              ticker: stockInfo.ticker,
              price: stockInfo.current_price,
              change: stockInfo.change,
              marketCap: stockInfo.marketCap,
              chartData: this.stockChartDataMap.get(stockInfo.ticker),
            };

            this.hoveredInfo = {
              category: stockInfo.industry,
              currentStock,
              stocks: this.stockData
                .filter(
                  (item) =>
                    item.industry === stockInfo.industry &&
                    item.sector === stockInfo.sector
                )
                .map((item) => ({
                  ticker: item.ticker,
                  price: item.current_price,
                  marketCap: item.marketCap,
                  change: item.change,
                  chartData: this.stockChartDataMap.get(item.ticker), // 使用預加載的數據
                })),
            };

            container.on("plotly_click", (data) => {
              if (!data || !data.points || !data.points[0]) return;

              const point = data.points[0];

              // 檢查是否為股票項目
              const isStockItem =
                point.data.text[point.pointNumber]?.includes("<br>");

              if (isStockItem) {
                // 如果是股票項目，則導航到 MovingAvgChart
                const stockInfo = this.stockData.find(
                  (item) => item.name === point.label
                );
                if (stockInfo) {
                  this.navigateToMovingAvg(stockInfo.ticker);
                }
              }

              const stockInfo = this.stockData.find(
                (item) => item.name === point.label
              );

              this.navigateToMovingAvg(stockInfo.ticker);
            });

            this.chartPosition = this.calculatePosition(data.event);
          });

          container.on("plotly_unhover", () => {
            if (!this.dataReady) return;
            // 重置邊框樣式
            Plotly.restyle(container, {
              "marker.line": [
                {
                  color: "rgba(255, 255, 255, 0.7)",
                  width: 1,
                },
              ],
            });
            this.hoveredInfo = null;
          });
        } catch (error) {
          console.error("Error setting up event listeners:", error);
        }
      },
      navigateToMovingAvg(symbol) {
        this.$router.push({ name: "MovingAvgChart", params: { symbol } });
      },
    },
    async created() {
      // 從 localStorage 加載快取
      try {
        const savedCache = localStorage.getItem("stockHeatmapCache");
        if (savedCache) {
          const { timestamp, data } = JSON.parse(savedCache);

          // 檢查是否需要更新快取
          if (!this.checkCacheExpiry(timestamp)) {
            this.cachedData = data;
            this.cacheExpiry = timestamp;
          }
        }
      } catch (e) {
        console.warn("Failed to restore cache from localStorage:", e);
      }
    },
    mounted() {
      this.preloadAllData();
      window.addEventListener("resize", this.renderHeatmap);
    },
    beforeUnmount() {
      // 清理事件監聽器
      window.removeEventListener("resize", this.renderHeatmap);
      if (this.$refs.heatmapContainer) {
        this.$refs.heatmapContainer.removeAllListeners("plotly_hover");
        this.$refs.heatmapContainer.removeAllListeners("plotly_unhover");
      }
    },
  };
</script>

<style scoped>
  /* 添加 loading overlay 樣式 */
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }

  .stock-heatmap {
    margin-top: 20px;
    position: relative;
  }

  .header-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1rem;
  }

  .reload-button {
    padding: 6px 12px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s;
  }

  .reload-button:hover {
    background-color: #357abd;
  }

  .heatmap-container {
    height: 800px;
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
    position: absolute; /* 確保使用固定定位 */
    z-index: 1000;
    background: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    min-width: 250px;
    max-width: 300px;
    max-height: 80vh; /* 限制最大高度 */
    font-size: 12px;
    display: flex;
    flex-direction: column;
  }

  .current-stock {
    padding: 6px;
    margin: -4px -4px 8px -4px;
    background: #333; /* 深色背景 */
    border-radius: 4px 4px 0 0;
    border-bottom: 2px solid #eee;
    color: #fff; /* 白色文字 */
  }

  .current-stock .stock-info {
    color: #fff;
  }

  .current-stock .price {
    color: #ddd;
  }

  .current-stock.positive-bg {
    background: #1b5e20; /* 深綠色背景 */
  }

  .current-stock.negative-bg {
    background: #b71c1c; /* 深紅色背景 */
  }

  .info-header {
    font-weight: bold;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
    margin-bottom: 8px;
  }

  .stocks-list {
    flex: 1;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .stock-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px;
  }

  .stock-item.current {
    background: #f0f0f0;
    font-weight: bold;
  }

  .stock-info {
    display: grid;
    grid-template-columns: 60px 70px 60px;
    gap: 8px;
    align-items: center;
  }

  .positive {
    color: #00c805;
  }

  .negative {
    color: #ff333a;
  }

  .ticker {
    font-weight: bold;
    font-size: 12px;
  }

  .change {
    font-size: 12px;
  }

  .price {
    color: #666;
    font-size: 12px;
  }
</style>
