<template>
  <div class="dialog-overlay" @click.self="$emit('cancel')">
    <div class="dialog-content">
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <div class="dialog-actions">
        <button class="btn-secondary" @click="$emit('cancel')">
          {{ cancelText }}
        </button>
        <button class="btn-primary" @click="$emit('confirm')">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      title: {
        type: String,
        default: "確認",
      },
      message: {
        type: String,
        required: true,
      },
      confirmText: {
        type: String,
        default: "確認",
      },
      cancelText: {
        type: String,
        default: "取消",
      },
    },
  };
</script>

<style scoped>
  .dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .dialog-content {
    background-color: #4F4F4F;
    padding: 24px;
    border-radius: 8px;
    width: 80%;
    max-width: 400px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }

  .dialog-content h3 {
    margin-top: 0;
    color: white;
    font-weight: bold;
    font-size: 25px;
  }

  .dialog-content p {
    color: white;
    margin-bottom: 20px;
  }

  .dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }

  .btn-primary,
  .btn-secondary {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
    border: none;
  }

  .btn-primary {
    background-color: #4a90e2;
    color: white;
  }

  .btn-primary:hover {
    background-color: #3a7bc8;
    transform: translateY(-2px);
  }

  .btn-secondary {
    background-color: #F0F0F0;
    color: #333;
  }

  .btn-secondary:hover {
    background-color: #e1e1e1;
    transform: translateY(-2px);
  }
</style>
