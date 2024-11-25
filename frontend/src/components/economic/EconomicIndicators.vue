// src/components/economic/EconomicIndicators.vue
<template>
  <div class="economic-indicators">
    <div class="indicators-header">
      <h3>經濟指標總覽</h3>
      <div class="time-selector">
        <select v-model="selectedYear">
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}年
          </option>
        </select>
      </div>
    </div>

    <div class="indicators-grid">
      <!-- GDP卡片 -->
      <div class="indicator-card">
        <div class="card-header">
          <h4>GDP變化</h4>
          <span :class="['change-badge', gdpTrend > 0 ? 'positive' : 'negative']">
            {{ gdpTrend > 0 ? '+' : '' }}{{ gdpTrend }}%
          </span>
        </div>
        <div class="chart-preview">
          <GDPChart :data="gdpData" :mini="true" />
        </div>
      </div>

      <!-- 失業率卡片 -->
      <div class="indicator-card">
        <div class="card-header">
          <h4>失業率</h4>
          <span :class="['change-badge', unemploymentTrend < 0 ? 'positive' : 'negative']">
            {{ unemploymentTrend > 0 ? '+' : '' }}{{ unemploymentTrend }}%
          </span>
        </div>
        <div class="chart-preview">
          <UnemploymentChart :data="unemploymentData" :mini="true" />
        </div>
      </div>

      <!-- 其他經濟指標 -->
      <div class="indicator-card">
        <h4>產業影響程度</h4>
        <div class="impact-list">
          <div v-for="(impact, industry) in industryImpact" 
               :key="industry" 
               class="impact-item">
            <span class="industry-name">{{ industry }}</span>
            <div class="impact-bar-container">
              <div class="impact-bar" 
                   :style="{ width: `${Math.abs(impact)}%`, 
                           backgroundColor: impact < 0 ? '#ff6b6b' : '#4caf50' }">
              </div>
            </div>
            <span class="impact-value">{{ impact }}%</span>
          </div>
        </div>
      </div>

      <!-- 經濟恢復指數 -->
      <div class="indicator-card">
        <h4>經濟恢復指數</h4>
        <div class="recovery-index">
          <div class="index-gauge">
            <svg viewBox="0 0 100 50">
              <path d="M10,40 A40,40 0 0,1 90,40" 
                    fill="none" 
                    stroke="#eee" 
                    stroke-width="5"/>
              <path :d="gaugeArc" 
                    fill="none" 
                    :stroke="recoveryColor" 
                    stroke-width="5"/>
            </svg>
            <div class="index-value">{{ recoveryIndex }}%</div>
          </div>
          <div class="recovery-status">{{ recoveryStatus }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import GDPChart from './GDPChart.vue'
import UnemploymentChart from './UnemploymentChart.vue';

export default {
  name: 'EconomicIndicators',
  components: {
    GDPChart,
    UnemploymentChart
  },
  data() {
    return {
      selectedYear: new Date().getFullYear(),
      industryImpact: {
        '觀光旅遊': -45.5,
        '餐飲服務': -30.2,
        '電子商務': 25.8,
        '製造業': -15.3,
        '金融服務': 5.6
      },
      recoveryIndex: 75
    }
  },
  computed: {
    ...mapState('economic', ['gdpData', 'unemploymentData']),
    
    availableYears() {
      return [2020, 2021, 2022, 2023, 2024]
    },
    
    gdpTrend() {
      if (!this.gdpData || this.gdpData.length < 2) return '數據不足';
      // 計算GDP年增率
      return ((this.gdpData[this.gdpData.length - 1]?.value || 0) - 
              (this.gdpData[this.gdpData.length - 2]?.value || 0)).toFixed(1)
    },
    
    unemploymentTrend() {
      if (!this.unemploymentData || this.unemploymentData.length < 2) return '數據不足';
      // 計算失業率變化
      return ((this.unemploymentData[this.unemploymentData.length - 1]?.value || 0) - 
              (this.unemploymentData[this.unemploymentData.length - 2]?.value || 0)).toFixed(1)
    },
    
    recoveryColor() {
      if (this.recoveryIndex >= 80) return '#4caf50'
      if (this.recoveryIndex >= 60) return '#ffd700'
      return '#ff6b6b'
    },
    
    recoveryStatus() {
      if (this.recoveryIndex >= 80) return '強勁復甦'
      if (this.recoveryIndex >= 60) return '穩定恢復'
      return '待改善'
    },
    
    gaugeArc() {
      const percentage = this.recoveryIndex / 100
      const x = 50 - 40 * Math.cos(percentage * Math.PI)
      const y = 40 - 40 * Math.sin(percentage * Math.PI)
      return `M10,40 A40,40 0 0,1 ${x},${y}`
    }
  },
  
  methods: {
    ...mapActions('economic', ['fetchEconomicData'])
  },
  
  mounted() {
    this.fetchEconomicData()
  }
}
</script>

<style scoped>
.economic-indicators {
  padding: 20px;
}

.indicators-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.indicator-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.change-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.9em;
}

.positive {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.negative {
  background-color: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
}

.impact-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.impact-item {
  display: grid;
  grid-template-columns: 100px 1fr 50px;
  align-items: center;
  gap: 10px;
}

.impact-bar-container {
  height: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.impact-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.recovery-index {
  text-align: center;
}

.index-gauge {
  position: relative;
  width: 200px;
  margin: 0 auto;
}

.index-value {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.5em;
  font-weight: bold;
}

.recovery-status {
  margin-top: 10px;
  font-weight: bold;
  color: #666;
}
</style>