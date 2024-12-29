<template>
    <button 
      class="logout-btn"
      @click="confirmLogout"
    >
      <span class="material-icons">logout</span>
      登出
    </button>
  </template>
  
  <script>
  export default {
    name: 'LogoutButton',
    methods: {
      confirmLogout() {
        if (confirm('確定要登出嗎？')) {
          this.$emit('click');
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .logout-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    background-color: #f44336;
    color: white;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 20px;
  }
  
  .logout-btn:hover {
    background-color: #d32f2f;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
  }
  
  .logout-btn .material-icons {
    font-size: 20px;
  }
  </style>