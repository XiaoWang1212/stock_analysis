<template>
    <div class="stock-app">
      
      <main>
        <router-view />
      </main>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StockApp',
  };
  </script>
  
  <style scoped>
  .stock-app {
    font-family: Arial, sans-serif;
    text-align: center;
  }
  
  /*header {
    background-color: #333;
    color: white;
    padding: 10px 0;
    margin-bottom: 20px;
  }*/
  
  main {
    display: flex;
    justify-content: center;
  }
  </style>