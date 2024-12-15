const CACHE_KEYS = {
    STOCK_HEATMAP: "stockHeatmapCache",
    STOCK_DATA: "stockDataCache_",
  };
  
  export const cacheManager = {
    // 檢查是否為同一天
    isSameDay(timestamp) {
      const cacheDate = new Date(timestamp);
      const today = new Date();
      return (
        cacheDate.getFullYear() === today.getFullYear() &&
        cacheDate.getMonth() === today.getMonth() &&
        cacheDate.getDate() === today.getDate()
      );
    },
  
    // 取得快取
    getCache(key) {
      try {
        const cache = localStorage.getItem(key);
        if (!cache) return null;
  
        const parsedCache = JSON.parse(cache);
        // 只檢查日期是否為同一天
        return this.isSameDay(parsedCache.timestamp) ? parsedCache.data : null;
      } catch {
        return null; // 無法解析快取，直接返回 null
      }
    },
  
    // 設定快取
    setCache(key, data) {
      if (!data) return;
  
      try {
        const cacheData = {
          timestamp: Date.now(),
          data: data,
        };
        localStorage.setItem(key, JSON.stringify(cacheData));
      } catch (e) {
        console.warn("Error setting cache:", e);
      }
    },
  
    // 清理過期快取
    checkAndCleanCache() {
      try {
        Object.values(CACHE_KEYS).forEach((key) => {
          const cache = localStorage.getItem(key);
          if (cache) {
            const parsedCache = JSON.parse(cache);
            // 如果不是同一天的快取，清除
            if (!this.isSameDay(parsedCache.timestamp)) {
              localStorage.removeItem(key);
              console.log(`Cache for ${key} cleared - outdated`);
            }
          }
        });
      } catch (e) {
        console.warn("Error checking cache:", e);
      }
    },
  };
  
  export { CACHE_KEYS };
  