import { createStore } from 'vuex'
import stockApp from './modules/stockApp'

const store = createStore({
  modules: {
    stockApp
  }
})

export default store