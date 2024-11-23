<template>
    <div class="birth-rate-view">
      <h1>出生率分析</h1>
      <birth-rate-chart />
      <birth-rate-analysis />
    </div>
  </template>
  
  <script>
  import BirthRateChart from '@/components/birth/BirthRateChart.vue'
  import BirthRateAnalysis from '@/components/birth/BirthRateAnalysis.vue'
  
  export default {
    name: 'BirthRateView',
    components: {
      BirthRateChart,
      BirthRateAnalysis
    }
  }
  </script>
  
  <style scoped>
  .birth-rate-view {
    padding: 20px;
  }
  
  h1 {
    margin-bottom: 20px;
    color: #333;
  }
  </style>