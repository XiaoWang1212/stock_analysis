// src/components/common/ErrorMessage.vue
<template>
  <div class="error-message">
    <div class="error-icon">⚠️</div>
    <p class="error-text">{{ message }}</p>
    <button v-if="retryable" @click="$emit('retry')" class="retry-button">
      重試
    </button>
  </div>
</template>

<script>
export default {
  name: 'ErrorMessage',
  props: {
    message: {
      type: String,
      required: true
    },
    retryable: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.error-message {
  color: black;
  text-align: center;
  padding: 20px;
  background-color: #fff3f3;
  border: 2px solid #ffcdd2;
  border-radius: 4px;
}

.error-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

.retry-button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>