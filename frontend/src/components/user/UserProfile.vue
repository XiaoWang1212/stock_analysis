<!-- UserProfile.vue -->
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
    props: {
      email: String,
      registrationDate: String
    }
  }
  </script>