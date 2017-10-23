import { get } from 'lodash'

import router from '../router'

const setRoute = ({zoom, lat, lng}) => {
  router.replace({query: {zoom, lat, lng}})
}

const getZoomFromState = (state) => +get(state, 'route.query.zoom')

const getLatFromState = (state) => +get(state, 'route.query.lat')

const getLngFromState = (state) => +get(state, 'route.query.lng')

export default {
  init (state) {
    state.zoom = getZoomFromState(state) || 16
    state.lat = getLatFromState(state) || 22.306
    state.lng = getLngFromState(state) || 114.163
  },
  setZoom (state, {zoom}) {
    state.zoom = zoom
    setRoute(state)
  },
  setCenter (state, {center: {lat, lng}}) {
    // console.log('setCenter', state.lat, lat, state.lat === lat, state.lng, lng, state.lng === lng)
    state.lat = lat
    state.lng = lng
    setRoute(state)
  },
  setLinks (state, {links}) {
    state.links = links
  },
  setWays (state, {ways}) {
    state.ways = ways
  },
  setNodes (state, {nodes}) {
    state.nodes = nodes
  }
}
