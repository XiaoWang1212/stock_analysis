import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import HomeView2 from '@/views/HomeView2.vue'
import StockApp from '@/views/StockApp.vue'
import MovingAvgChart from '@/components/stock/MovingAvgChart.vue'
import StockHeatMap from '@/components/stock/StockHeatmap.vue'
import LoginView from '@/views/LoginView.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView,
    meta: {
      hideHeader: true
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView
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
  },
  {
    path: '/home2',
    name: 'Home2',
    component: HomeView2
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router