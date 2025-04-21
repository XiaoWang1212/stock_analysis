// src/services/api.js
const API_BASE_URL =
  process.env.VUE_APP_API_BASE_URL || "http://localhost:5000";

export const apiService = {
  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  // Stock endpoints
  stock: {
    getStockData: (symbol, market = "US") => {
      if (market === "US") {
        return apiService.get(`/stock_app/api/stock_data/${symbol}`);
      } else {
        return apiService.get(`/stock_app/api/tw_stock_data/${symbol}`);
      }
    },
    getSMAData: (symbol, market = "US") => {
      if (market === "US") {
        return apiService.get(`/stock_app/api/ma/${symbol}`);
      } else {
        return apiService.get(`/stock_app/api/tw_ma/${symbol}`);
      }
    },
    getBIASData: (symbol, market = "US") => {
      if (market === "US") {
        return apiService.get(`/stock_app/api/bias/${symbol}`);
      } else {
        return apiService.get(`/stock_app/api/tw_bias/${symbol}`);
      }
    },
    predictStockPrice: (symbol, market = "US") =>
      apiService.get(`/stock_app/api/lstm_predict/${symbol}/${market}`),
    getStockCategories: (market = "US") => {
      if (market === "US") {
        return apiService.get("/stock_app/api/categories");
      } else {
        return apiService.get("/stock_app/api/tw_categories");
      }
    },
    getTwCategories: async () => {
      try {
        // 直接使用 fetch 獲取原始文本
        const response = await fetch("/stock_app/api/tw_categories");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 獲取文本並清理 NaN 值
        const text = await response.text();
        const cleanedText = text
          .replace(/"name"\s*:\s*NaN/g, '"name": null')
          .replace(/"[^"]*":\s*NaN/g, "$&: null");

        // 手動解析 JSON
        return JSON.parse(cleanedText);
      } catch (error) {
        console.error("Error fetching TW categories:", error);
        throw error;
      }
    },
  },
};
