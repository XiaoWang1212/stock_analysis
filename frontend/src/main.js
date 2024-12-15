import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import { cacheManager } from './services/cacheManager';

// 應用啟動時檢查快取
cacheManager.checkAndCleanCache();

createApp(App).use(store).use(router).mount('#app')
