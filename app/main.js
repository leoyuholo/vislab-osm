import Vue from 'vue'
import { sync } from 'vuex-router-sync'
import * as VueGoogleMaps from 'vue2-google-maps'

import store from './store'
import router from './router'

Vue.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyCLhtfQgPadHIHJDOp3s3-DvmYx60pELIM',
    libraries: 'places,drawing,visualization'
  }
})

const unsync = sync(store, router)

const app = new Vue({
  router,
  el: '#app',
  store,
  created () {
    this.$store.dispatch('init')
  }
})
