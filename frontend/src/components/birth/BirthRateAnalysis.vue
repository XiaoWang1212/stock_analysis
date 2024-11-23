// src/components/birth/BirthRateAnalysis.vue
<template>
  <div class="birth-rate-analysis">
    <div class="analysis-header">
      <h3>出生率分析報告</h3>
      <div class="time-range-selector">
        <select v-model="selectedTimeRange" @change="updateAnalysis">
          <option value="1">過去一年</option>
          <option value="3">過去三年</option>
          <option value="5">過去五年</option>
        </select>
      </div>
    </div>

    <div class="analysis-content">
      <div class="analysis-card">
        <h4>整體趨勢</h4>
        <p>{{ overallTrend }}</p>
      </div>

      <div class="analysis-card">
        <h4>影響因素</h4>
        <ul>
          <li v-for="(factor, index) in impactFactors" :key="index">
            {{ factor }}
          </li>
        </ul>
      </div>

      <div class="analysis-card">
        <h4>地區比較</h4>
        <table>
          <thead>
            <tr>
              <th>地區</th>
              <th>變化幅度</th>
              <th>趨勢</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(region, index) in regionalComparison" :key="index">
              <td>{{ region.name }}</td>
              <td>{{ region.change }}%</td>
              <td>{{ region.trend }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BirthRateAnalysis',
  data() {
    return {
      selectedTimeRange: '1',
      overallTrend: '',
      impactFactors: [],
      regionalComparison: []
    }
  },
  methods: {
    updateAnalysis() {
      // 這裡可以根據選擇的時間範圍更新分析數據
      // 實際應用中應該從API獲取數據
      this.overallTrend = '受疫情影響，出生率呈現持續下降趨勢...'
      this.impactFactors = [
        '疫情期間醫療資源調配',
        '經濟不確定性增加',
        '居家隔離政策影響',
        '婚育決策延後'
      ]
      this.regionalComparison = [
        { name: '北部', change: -5.2, trend: '下降' },
        { name: '中部', change: -4.8, trend: '下降' },
        { name: '南部', change: -4.5, trend: '下降' },
        { name: '東部', change: -3.9, trend: '下降' }
      ]
    }
  },
  mounted() {
    this.updateAnalysis()
  }
}
</script>

<style scoped>
.birth-rate-analysis {
  padding: 20px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.analysis-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.analysis-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.analysis-card h4 {
  margin-bottom: 15px;
  color: #333;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
}

select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
}

li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #2196f3;
}
</style>