// src/services/api.js
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000'

export const apiService = {
  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  },

  // API endpoints
  birthRate: {
    getYearlyData: () => apiService.get('/birth-rate/yearly'),
    getComparison: () => apiService.get('/birth-rate/comparison')
  },
  
  deathRate: {
    getYearlyData: () => apiService.get('/death-rate/yearly'),
    getComparison: () => apiService.get('/death-rate/comparison')
  },
  
  economic: {
    getGDP: () => apiService.get('/economic/gdp'),
    getUnemployment: () => apiService.get('/economic/unemployment'),
    getIndicators: () => apiService.get('/economic/indicators')
  },

  // Stock endpoints
  stock: {
    getStockData: (symbol) => apiService.get(`/stock_app/api/stock_data/${symbol}`),
    getSMAData: (symbol) => apiService.get(`/stock_app/api/ma/${symbol}`),
    getBIASData: (symbol) => apiService.get(`/stock_app/api/bias/${symbol}`),
    predictStockPrice: (symbol) => apiService.get(`/stock_app/api/predict/${symbol}`),
    getStockCategories: () => apiService.get('/stock_app/api/categories'),
  }
}