<template>
  <div class="moving-avg-chart">
    <h2>{{ symbol }} Moving Averages Chart</h2>
    <div class="chart-selector">
      <label>
        <input type="checkbox" v-model="showSMA" /> SMA
      </label>
      <label>
        <input type="checkbox" v-model="showEMA" /> EMA
      </label>
      <label>
        <input type="checkbox" v-model="showWMA" /> WMA
      </label>
      <label>
        <input type="checkbox" v-model="showKAMA" /> KAMA
      </label>
    </div>
    <div class="chart-container">
      <SMAChart v-if="showSMA" :symbol="symbol" />
      <EMAChart v-if="showEMA" :symbol="symbol" />
      <WMAChart v-if="showWMA" :symbol="symbol" />
      <KAMAChart v-if="showKAMA" :symbol="symbol" />
      <div class="analysis-selector">
        <button @click="selectAnalysis('BIAS')" :class="{ active: selectedAnalysis === 'BIAS' }">BIAS</button>
        <button @click="selectAnalysis('RSI')" :class="{ active: selectedAnalysis === 'RSI' }">RSI</button>
        <button @click="selectAnalysis('STOCH')" :class="{ active: selectedAnalysis === 'STOCH' }">STOCH</button>
        <button @click="selectAnalysis('STOCHRSI')" :class="{ active: selectedAnalysis === 'STOCHRSI' }">STOCH RSI</button>
        <button @click="selectAnalysis('STOCHF')" :class="{ active: selectedAnalysis === 'STOCHF' }">STOCH F</button>
        <button @click="selectAnalysis('MACD')" :class="{ active: selectedAnalysis === 'MACD' }">MACD</button>
      </div>
      <div class="analysis-container">
        <SMAAndBIASChart v-if="selectedAnalysis === 'BIAS'" :symbol="symbol" />
        <RSIChart v-else-if="selectedAnalysis === 'RSI'" :symbol="symbol" />
        <STOCHChart v-else-if="selectedAnalysis === 'STOCH'" :symbol="symbol" />
        <STOCHRSIChart v-else-if="selectedAnalysis === 'STOCHRSI'" :symbol="symbol" />
        <STOCHFChart v-else-if="selectedAnalysis === 'STOCHF'" :symbol="symbol" />
        <MACDChart v-else-if="selectedAnalysis === 'MACD'" :symbol="symbol" />
      </div>
    </div>
  </div>
</template>

<script>
import SMAChart from './movingAvg/SMAChart.vue';
import EMAChart from './movingAvg/EMAChart.vue';
import WMAChart from './movingAvg/WMAChart.vue';
import KAMAChart from './movingAvg/KAMAChart.vue';
import SMAAndBIASChart from './movingAvg/SMAAndBIASChart.vue';
import RSIChart from './momentum/RSIChart.vue';
import STOCHChart from './momentum/STOCHChart.vue';
import STOCHRSIChart from './momentum/STOCHRSIChart.vue';
import STOCHFChart from './momentum/STOCHFChart.vue';
import MACDChart from './momentum/MACDChart.vue';

export default {
  components: {
    SMAChart,
    EMAChart,
    WMAChart,
    KAMAChart,
    SMAAndBIASChart,
    RSIChart,
    STOCHChart,
    STOCHRSIChart,
    STOCHFChart,
    MACDChart
  },
  props: {
    symbol: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      showSMA: true,
      showEMA: false,
      showWMA: false,
      showKAMA: false,
      selectedAnalysis: 'BIAS'
    };
  },
  methods: {
    selectAnalysis(analysis) {
      this.selectedAnalysis = analysis;
    }
  }
};
</script>

<style scoped>
.moving-avg-chart {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.chart-selector {
  margin-bottom: 20px;
}

.chart-selector label {
  margin-right: 10px;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-selector {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.analysis-selector button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
  margin: 0 5px;
}

.analysis-selector button.active {
  background-color: #0056b3;
}

.analysis-selector button:hover {
  background-color: #0056b3;
}

.analysis-container {
  margin-top: 20px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>