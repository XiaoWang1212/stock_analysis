export default {
    namespaced: true,
    state: {
      economicIndicators: [],
      loading: false,
      error: null,
    },
    mutations: {
      SET_INDICATORS(state, data) {
        state.economicIndicators = data;
      },
      SET_LOADING(state, status) {
        state.loading = status;
      },
      SET_ERROR(state, error) {
        state.error = error;
      },
    },
    actions: {
      async fetchIndicators({ commit }) {
        commit("SET_LOADING", true);
        try {
          const response = await fetch("/api/economic-indicators");
          const data = await response.json();
          commit("SET_INDICATORS", data);
          commit("SET_ERROR", null);
        } catch (error) {
          commit("SET_ERROR", error.message);
        } finally {
          commit("SET_LOADING", false);
        }
      },
    },
    getters: {
      getIndicators: (state) => state.economicIndicators,
      getLoading: (state) => state.loading,
      getError: (state) => state.error,
    },
  };