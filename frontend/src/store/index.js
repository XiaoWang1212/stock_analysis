import { createStore } from 'vuex'
import birthRate from './modules/birthRate'
import deathRate from './modules/deathRate'
import economic from './modules/economic'

const store = createStore({
  modules: {
    birthRate,
    deathRate,
    economic
  }
})

export default store