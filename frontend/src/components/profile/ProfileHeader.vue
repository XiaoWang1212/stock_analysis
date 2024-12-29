<template>
  <div class="profile-section">
    <div class="profile-header">
      <span class="material-icons profile-icon">account_circle</span>
      <h2>個人資料</h2>
    </div>

    <div class="profile-info">
      <div class="info-item">
        <span class="label">電子信箱</span>
        <span class="value">{{ email }}</span>
      </div>
      <div class="info-item">
        <span class="label">註冊日期</span>
        <span class="value">{{ registrationDate }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileHeader',
  props: {
    email: {
      type: String,
      required: true
    },
    registrationDate: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.profile-section {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.profile-header h2 {
  font-size: 1.8em;
  color: #2c3e50;
  margin: 0;
}

.profile-icon {
  font-size: 48px;
  color: #4a90e2;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.label {
  color: #666;
  font-weight: 500;
}

.value {
  color: #333;
}

@media (max-width: 768px) {
  .profile-header h2 {
    font-size: 1.5em;
  }
}
</style>