<template>
  <div class="home">
    <h1>COVID-19 影響分析</h1>
    <div class="dashboard-grid">
      <router-link to="/birth-rate" class="dashboard-item">
        <h2>出生率影響</h2>
        <birth-rate-chart v-if="birthRateData.length" :data="birthRateData" />
      </router-link>
      
      <router-link to="/death-rate" class="dashboard-item">
        <h2>死亡率影響</h2>
        <death-rate-chart v-if="deathRateData.length" :data="deathRateData" />
      </router-link>
      
      <router-link to="/economic-impact" class="dashboard-item">
        <h2>經濟影響</h2>
        <economic-indicators v-if="economicData.length" :data="economicData" />
      </router-link>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import BirthRateChart from '@/components/birth/BirthRateChart.vue'
import DeathRateChart from '@/components/death/DeathRateChart.vue'
import EconomicIndicators from '@/components/economic/EconomicIndicators.vue'

export default {
  name: 'HomeView',
  components: {
    BirthRateChart,
    DeathRateChart,
    EconomicIndicators
  },
  computed: {
    ...mapState('birthRate', {
      birthRateData: state => state.yearlyData
    }),
    ...mapState('deathRate', {
      deathRateData: state => state.yearlyData
    }),
    ...mapState('economic', {
      economicData: state => state.economicIndicators
    })
  },
  created() {
    this.fetchAllData()
  },
  methods: {
    ...mapActions('birthRate', {
      fetchBirthRate: 'fetchData'
    }),
    ...mapActions('deathRate', {
      fetchDeathRate: 'fetchData'
    }),
    ...mapActions('economic', {
      fetchIndicators: 'fetchIndicators'
    }),
    async fetchAllData() {
      await Promise.all([
        this.fetchBirthRate(),
        this.fetchDeathRate(),
        this.fetchIndicators()
      ])
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

.dashboard-item {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-5px);
  }
}
</style>