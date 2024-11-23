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
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router