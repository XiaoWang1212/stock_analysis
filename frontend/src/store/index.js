import { createStore } from 'vuex'
import birthRate from './modules/birthRate'
import deathRate from './modules/deathRate'
import economic from './modules/economic'
import stockApp from './modules/stockApp'

const store = createStore({
  modules: {
    birthRate,
    deathRate,
    economic,
    stockApp
  }
})

export default store