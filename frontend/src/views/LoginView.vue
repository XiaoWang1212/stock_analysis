<template>
  <div class="container">
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 添加直接訪問按鈕 -->
    <div class="guest-access">
      <button class="guest-button" @click="accessAsGuest">
        <span>訪客模式</span>
        <span class="material-symbols-outlined"> accessibility </span>
      </button>
    </div>

    <div class="forms-container" :class="{ 'sign-up-mode': isSignUp }">
      <div class="left-panel">
        <form
          :class="{ active: !isSignUp }"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <h2>登入</h2>
          <input type="text" v-model="username" placeholder="帳號" required />
          <input
            type="password"
            v-model="password"
            placeholder="密碼"
            required
          />
          <button type="submit">登入</button>
        </form>
        <form
          :class="{ active: isSignUp }"
          @submit.prevent="handleRegister"
          class="register-form"
        >
          <h2>註冊</h2>
          <input
            type="email"
            v-model="registerEmail"
            placeholder="電子信箱"
            required
          />
          <input
            type="password"
            v-model="registerPassword"
            placeholder="密碼"
            required
            minlength="6"
          />
          <input
            type="password"
            v-model="confirmPassword"
            placeholder="確認密碼"
            required
          />
          <button type="submit">註冊</button>
        </form>
      </div>

      <div class="right-panel">
        <div :class="{ active: !isSignUp }" class="info-panel">
          <h2>還沒有帳號？</h2>
          <p>立即註冊開始使用我們的服務！</p>
          <button @click="isSignUp = true">註冊帳號</button>
        </div>
        <div :class="{ active: isSignUp }" class="info-panel">
          <h2>已經有帳號了？</h2>
          <p>請登入繼續使用我們的服務！</p>
          <button @click="isSignUp = false">返回登入</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { clearAuthData } from "@/utils/auth";
  export default {
    data() {
      return {
        isSignUp: false,
        username: "",
        password: "",
        registerEmail: "",
        registerPassword: "",
        confirmPassword: "",
        message: "",
        messageType: "error",
      };
    },
    methods: {
      accessAsGuest() {
        clearAuthData();

        localStorage.setItem("guestMode", "true");

        this.$router.push("/stock-app");
      },
      async handleLogin() {
        try {
          const response = await fetch("http://localhost:5000/login", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: this.username,
              password: this.password,
            }),
          });

          const data = await response.json();

          if (response.ok) {
            // 先清除舊的資料
            clearAuthData();

            const loginTime = new Date().getTime();
            const expirationTime = loginTime + data.expiresIn * 1000; // 轉換為毫秒並加上當前時間

            // 儲存 JWT token
            sessionStorage.setItem("loginTime", loginTime);
            sessionStorage.setItem("token", data.token);
            sessionStorage.setItem("tokenExpiration", expirationTime);

            // 儲存用戶資訊
            localStorage.setItem("userId", data.userId);
            localStorage.setItem("userEmail", data.email);
            localStorage.setItem("registrationDate", data.registrationDate);

            this.message = "登入成功";
            this.messageType = "success";

            setTimeout(() => {
              this.$router.push("/home");
            }, 1000);
          } else {
            this.message = data.error;
            this.messageType = "error";
          }
        } catch (error) {
          this.message = "登入時發生錯誤";
          this.messageType = "error";
        }
      },

      async handleRegister() {
        if (this.registerPassword !== this.confirmPassword) {
          this.message = "密碼不匹配";
          this.messageType = "error";
          return;
        }

        try {
          const response = await fetch("http://localhost:5000/register", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: this.registerEmail,
              password: this.registerPassword,
            }),
          });

          const data = await response.json();

          if (response.ok) {
            // 註冊成功，切換到登入
            // 儲存 userId
            localStorage.setItem("userId", data.userId);
            localStorage.setItem("userEmail", this.registerEmail);
            localStorage.setItem(
              "registrationDate",
              new Date().toISOString().split("T")[0]
            );

            this.message = "註冊成功，請登入";
            this.messageType = "success";
            this.isSignUp = false;
          } else {
            this.message = data.error;
            this.messageType = "error";
          }
        } catch (error) {
          this.message = "註冊時發生錯誤";
          this.messageType = "error";
        }
      },
    },
  };
</script>

<style scoped>
  .message {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    border-radius: 4px;
    font-size: 14px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: fadeIn 0.3s ease;
  }

  .error {
    background-color: #ff6b6b;
    color: white;
  }

  .success {
    background-color: #4caf50;
    color: white;
  }

  .guest-access {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 100;
  }

  .guest-button {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    background: #f8f9fa;
    border: 2px solid #4a90e2;
    color: #4a90e2;
    border-radius: 25px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .guest-button:hover {
    background: #4a90e2;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .guest-button i {
    transition: transform 0.3s ease;
  }

  .guest-button:hover i {
    transform: translateX(5px);
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translate(-50%, -10px);
    }
    to {
      opacity: 1;
      transform: translate(-50%, 0);
    }
  }

  .container {
    height: 100vh;
    position: relative;
    width: 100%;
    min-height: calc(100vh - 60px);
    background: #272727;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .forms-container {
    position: relative;
    width: 900px;
    height: 500px;
    background: #F0F0F0;
    border-radius: 10px;
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25);
    display: flex;
    overflow: hidden;
  }

  .left-panel,
  .right-panel {
    position: absolute;
    top: 0;
    height: 100%;
    width: 50%;
    transition: transform 0.6s ease-in-out;
  }

  .left-panel {
    left: 0;
    background: #5b5b5b;
    color: white;
    z-index: 2;
  }

  .right-panel {
    left: 50%;
    background: #66B3FF;
    color: white;
  }

  /* 滑動效果 */
  .forms-container.sign-up-mode .left-panel {
    transform: translateX(100%);
  }

  .forms-container.sign-up-mode .right-panel {
    transform: translateX(-100%);
  }

  /* 表單切換動畫 */
  form,
  .info-panel {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 20px;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.8s ease, visibility 0.8s ease;
  }

  form.active,
  .info-panel.active {
    opacity: 1;
    visibility: visible;
  }

  /* 按鈕樣式 */
  button {
    width: 130px;
    padding: 12px;
    border: none;
    border-radius: 25px;
    background: #66B3FF;
    color: #fff;
    font-size: 14px;
    cursor: pointer;
    transition: transform 0.3s ease;
  }

  .right-panel button {
    background: transparent;
    border: 2px solid #fff;
  }

  button:hover {
    transform: scale(1.05);
  }

  input {
    width: 100%;
    max-width: 300px;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 25px;
    outline: none;
    font-size: 14px;
    background-color: #F0F0F0;
  }

  input:focus{
    border: 2px solid #66B3FF;
  }

  h2 {
    margin-bottom: 10px;
    color: inherit;
  }

  p {
    text-align: center;
    margin-bottom: 20px;
  }
</style>
