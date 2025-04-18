import { apiService } from "@/services/api";

const state = {
  currentMarket: "US",
  loading: false,
  error: null,
  stockData: [],
  chartData: null,
  predictedPrice: null,
  categoriesLoaded: {
    US: false,
    TW: false,
  },
};

const mutations = {
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_STOCK_DATA(state, { data, market = "US" }) {
    state.stockData = data;
    state.categoriesLoaded[market] = true;
  },
  SET_CHART_DATA(state, data) {
    state.chartData = data;
  },
  SET_PREDICTED_PRICE(state, price) {
    state.predictedPrice = price;
  },
  RESET_PREDICTED_PRICE(state) {
    state.predictedPrice = null;
  },
  SET_CURRENT_MARKET(state, market) {
    state.currentMarket = market;
  },
};

const actions = {
  setCurrentMarket({ commit }, market) {
    commit("SET_CURRENT_MARKET", market);
    localStorage.setItem("selectedMarket", market);
  },
  async fetchStockCategories({ commit, state }, { force = false } = {}) {
    const market = state.currentMarket;

    if (!force && state.categoriesLoaded[market] && state.stockData.length > 0) {
      return state.stockData;
    }

    commit("SET_LOADING", true);
    commit("SET_ERROR", null);

    try {
      let data;
      if (market === "US") {
        data = await apiService.stock.getStockCategories();
      } else {
        data = await apiService.stock.getTwCategories();
      }

      commit("SET_STOCK_DATA", { data, market });
      return data;
    } catch (error) {
      commit(
        "SET_ERROR",
        `無法獲取${market === "US" ? "美股" : "台股"}分類資料`
      );
      throw error;
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async fetchStockData({ commit, state }, symbol) {
    if (!symbol) return;

    const market = state.currentMarket;
    commit("SET_LOADING", true);
    commit("SET_ERROR", null);

    try {
      let data;

      if (market === "US") {
        data = await apiService.stock.getSMAData(symbol);
      } else {
        data = await apiService.stock.getTwMaData(symbol);
      }

      if (!data || !data.dates) {
        throw new Error(`獲取 ${symbol} 的均線數據失敗`);
      }

      commit("SET_STOCK_DATA", data.stocks);
      return data;
    } catch (error) {
      commit("SET_ERROR", "Failed to fetch stock data");
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async fetchStockChartData({ commit, state }, symbol) {
    if (!symbol) return;

    const market = state.currentMarket;

    commit("SET_LOADING", true);
    commit("SET_ERROR", null);

    try {
      let data;

      if (market === "US") {
        data = await apiService.stock.getStockData(symbol);
      } else {
        data = await apiService.stock.getTwStockData(symbol);
      }

      commit("SET_CHART_DATA", data);
      return data;
    } catch (error) {
      console.error(`Error fetching chart data for ${symbol}:`, error);
      commit(
        "SET_ERROR",
        `無法獲取 ${symbol} 的ChartData數據: ${error.message}`
      );
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async fetchSMAChartData({ commit }, symbol) {
    if (!symbol) return;

    const market = state.currentMarket;

    commit("SET_LOADING", true);
    commit("SET_ERROR", null);

    try {
      let data;

      if (market === "US") {
        data = await apiService.stock.getSMAData(symbol);
      } else {
        data = await apiService.stock.getTwMaData(symbol);
      }

      // 清理和驗證數據
      const cleanedData = {
        ...data,
        values: Array.isArray(data.values)
          ? data.values.map((val) =>
              val === null || val === "NaN" || Number.isNaN(val) ? null : val
            )
          : [],
      };

      commit("SET_CHART_DATA", cleanedData);
      return cleanedData;
    } catch (error) {
      commit("SET_ERROR", error.message || "Failed to fetch SMA data");
      return null;
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async fetchBIASChartData({ commit }, symbol) {
    if (!symbol) return;

    const market = state.currentMarket;

    commit("SET_LOADING", true);
    commit("SET_ERROR", null);

    try {
      let data;

      if (market === "US") {
        data = await apiService.stock.getBIASData(symbol);
      } else {
        data = await apiService.stock.getTwBiasData(symbol);
      }

      if (!data || !data.dates || !data.bias_10) {
        throw new Error(`獲取 ${symbol} 的乖離率數據格式不完整`);
      }

      commit("SET_CHART_DATA", data);
      return data;
    } catch (error) {
      console.error(
        `Error fetching BIAS chart data for ${symbol} (${market}):`,
        error
      );
      commit("SET_ERROR", `無法獲取 ${symbol} 的乖離率數據: ${error.message}`);
      throw error;
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async predictStockPrice({ commit }, symbol) {
    commit("SET_LOADING", true);
    commit("SET_ERROR", null);
    try {
      const data = await apiService.stock.predictStockPrice(symbol);
      if (data.error) {
        commit("SET_ERROR", data.error);
        return data;
      } else {
        commit("SET_PREDICTED_PRICE", data.predicted_price);
      }
    } catch (error) {
      commit("SET_ERROR", "Failed to predict stock price");
    } finally {
      commit("SET_LOADING", false);
    }
  },
  resetPredictedPrice({ commit }) {
    commit("RESET_PREDICTED_PRICE");
  },
  resetChartData({ commit }) {
    commit("SET_CHART_DATA", null);
  },
};

const getters = {
  currentMarket: (state) => state.currentMarket,
  loading: (state) => state.loading,
  error: (state) => state.error,
  stockData: (state) => state.stockData,
  chartData: (state) => state.chartData,
  predictedPrice: (state) => state.predictedPrice,
  stockList: (state) => {
    if (!state.stockData.length) return [];

    if (state.currentMarket === "US") {
      return state.stockData.map((stock) => stock.ticker || stock.symbol);
    } else {
      const stockList = [];
      state.stockData.forEach((category) => {
        category.stocks.forEach((stock) => {
          stockList.push(stock.ticker);
        });
      });
      return stockList;
    }
  },
  categories: (state) => state.stockData || [],
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
