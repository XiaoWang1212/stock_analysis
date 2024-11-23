// src/services/api.js
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000/api'

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
  }
}