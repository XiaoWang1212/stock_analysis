import axios from "axios";

const state = {
  loading: false,
  error: null,
  stockData: [],
  chartData: null,
  predictedPrice: null,
};

const mutations = {
  SET_LOADING(state, status) {
    state.loading = status;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_STOCK_DATA(state, data) {
    state.stockData = data;
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
};

const actions = {
  async fetchStockData({ commit }) {
    commit("SET_LOADING", true);
    commit("SET_ERROR", null);
    try {
      const response = await axios.get("/stock_app/api/data");
      commit("SET_STOCK_DATA", response.data.stocks);
    } catch (error) {
      commit("SET_ERROR", "Failed to fetch stock data");
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async fetchStockChartData({ commit }, symbol) {
    commit("SET_LOADING", true);
    commit("SET_ERROR", null);
    try {
      const response = await axios.get(`stock_app/api/stock_data/${symbol}`);
      if (response.data.error) {
        commit("SET_ERROR", response.data.error);
        return response.data;
      } else {
        commit("SET_CHART_DATA", response.data);
        return response.data;
      }
    } catch (error) {
      commit("SET_ERROR", "Failed to fetch stock chart data");
    } finally {
      commit("SET_LOADING", false);
    }
  },
  async predictStockPrice({ commit }, symbol) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await axios.get(`stock_app/api/predict/${symbol}`);
      if (response.data.error) {
        commit('SET_ERROR', response.data.error);
        return response.data;
      } else {
        commit('SET_PREDICTED_PRICE', response.data.predicted_price);
      }
    } catch (error) {
      commit('SET_ERROR', 'Failed to predict stock price');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  resetPredictedPrice({ commit }) {
    commit('RESET_PREDICTED_PRICE');
  },
};

const getters = {
  loading: (state) => state.loading,
  error: (state) => state.error,
  stockData: (state) => state.stockData,
  chartData: (state) => state.chartData,
  predictedPrice: (state) => state.predictedPrice
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
