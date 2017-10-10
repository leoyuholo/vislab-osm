import Vue from 'vue'
import Vuex from 'vuex'

import actions from './actions'
import getters from './getters'
import mutations from './mutations'
import router from '../router'

Vue.use(Vuex)

const state = {
  zoom: null,
  lat: null,
  lng: null,
  links: null
}

const store = new Vuex.Store({
  state,
  getters,
  actions,
  mutations
})

export default store
