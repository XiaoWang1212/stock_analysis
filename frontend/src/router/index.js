import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BirthRateView from '../views/BirthRateView.vue'
import DeathRateView from '../views/DeathRateView.vue'
import EconomicView from '../views/EconomicView.vue'
import StockApp from '../views/StockApp.vue'
import MovingAvgChart from '../components/stock/MovingAvgChart.vue'
import StockHeatMap from '../components/stock/StockHeatmap.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/birth-rate',
    name: 'BirthRate',
    component: BirthRateView
  },
  {
    path: '/death-rate',
    name: 'DeathRate',
    component: DeathRateView
  },
  {
    path: '/economic-impact',
    name: 'EconomicImpact',
    component: EconomicView
  },
  {
    path: '/stock-app',
    name: 'StockApp',
    component: StockApp
  },
  {
    path: '/moving-avg/:symbol',
    name: 'MovingAvgChart',
    component: MovingAvgChart,
    props: true
  },
  {
    path: '/stock-heatmap',
    name: 'StockHeatMap',
    component: StockHeatMap
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router