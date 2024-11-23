<template>
    <div class="economic-view">
      <h1>經濟影響分析</h1>
      <GDPChart />
      <unemployment-chart />
      <economic-indicators />
    </div>
  </template>
  
  <script>
  import GDPChart from '@/components/economic/GDPChart.vue'
  import UnemploymentChart from '@/components/economic/UnemploymentChart.vue'
  import EconomicIndicators from '@/components/economic/EconomicIndicators.vue'
  
  export default {
    name: 'EconomicView',
    components: {
      GDPChart,
      UnemploymentChart,
      EconomicIndicators
    }
  }
  </script>
  
  <style scoped>
  .economic-view {
    padding: 20px;
  }
  
  h1 {
    margin-bottom: 20px;
    color: #333;
  }
  </style>