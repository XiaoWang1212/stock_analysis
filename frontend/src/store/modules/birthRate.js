// src/store/modules/birthRate.js
export default {
  namespaced: true,
  state: {
    yearlyData: [],
    comparisonData: null,
    loading: false,
    error: null,
  },
  mutations: { 
    SET_DATA(state, data) {
      state.yearlyData = data;
    },
    SET_COMPARISON(state, data) {
      state.comparisonData = data;
    },
    SET_LOADING(state, status) {
      state.loading = status;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
  },
  actions: {
    async fetchData({ commit }) {
      commit("SET_LOADING", true);
      try {
        const response = await fetch("/api/birth-rate");
        const data = await response.json();
        commit("SET_DATA", data);
        commit("SET_ERROR", null);
      } catch (error) {
        commit("SET_ERROR", error.message);
      } finally {
        commit("SET_LOADING", false);
      }
    },
  },
  getters: {
    getData: (state) => state.yearlyData,
    getLoading: (state) => state.loading,
    getError: (state) => state.error,
    getComparison: (state) => state.comparisonData,
  },
};
