<template>
    <div class="group-header">
      <input
        v-model="groupName"
        @change="$emit('update-name', groupName)"
        class="group-name-input"
        :placeholder="`群組 ${index + 1}`"
        @click.stop
      />
      <button @click.stop="$emit('add-stock')" class="add-stock-btn">
        <span class="material-icons">add</span>
        添加股票
      </button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'GroupHeader',
    props: {
      name: String,
      index: Number
    },
    emits: ['update-name', 'add-stock'],
    data() {
      return {
        groupName: this.name
      }
    },
    watch: {
      name(newVal) {
        this.groupName = newVal;
      }
    }
  }
  </script>
  
  <style scoped>
  .group-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
    padding-right: 40px;
    gap: 10px;
  }
  
  .group-name-input {
    font-size: 1em;
    color: #2c3e50;
    background: white;
    transition: border-color 0.3s ease;
    padding: 8px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
  }

  .group-name-input:focus {
    border-color: #4a90e2;
    outline: none;
  }
  
  .add-stock-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 10px 15px;
    background: #4a90e2;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1em;
    transition: all 0.3s ease;
  }

  .add-stock-btn:hover {
    background: #357abd;
    transform: translateY(-1px);
    transition: all 0.3s ease;
  }

  .add-stock-btn{
    pointer-events: auto;
  }
  </style>