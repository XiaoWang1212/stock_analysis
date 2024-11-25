import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/birth-rate',
    name: 'BirthRate',
    component: () => import('../views/BirthRateView.vue')
  },
  {
    path: '/death-rate',
    name: 'DeathRate',
    component: () => import('../views/DeathRateView.vue')
  },
  {
    path: '/economic-impact',
    name: 'EconomicImpact',
    component: () => import('../views/EconomicView.vue')
  },
  {
    path: '/stock-app',
    name: 'StockApp',
    component: () => import('../views/StockApp.vue')
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router