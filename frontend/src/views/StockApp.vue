<template>
    <div class="stock-app">
      <header>
        <h1>Stock Application</h1>
      </header>
      <main>
        <stock-analysis />
      </main>
    </div>
  </template>
  
  <script>
  import StockAnalysis from '@/components/stock/StockAnalysis.vue';
  
  export default {
    name: 'StockApp',
    components: {
      StockAnalysis
    }
  };
  </script>
  
  <style scoped>
  .stock-app {
    font-family: Arial, sans-serif;
    text-align: center;
    padding: 20px;
  }
  
  header {
    background-color: #333;
    color: white;
    padding: 10px 0;
    margin-bottom: 20px;
  }
  
  main {
    display: flex;
    justify-content: center;
  }
  </style>