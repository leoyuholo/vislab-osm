
const postOptions = (bodyObj) => {
  return {
    method: 'post',
    headers: new Headers({'Content-Type': 'application/json'}),
    body: JSON.stringify(bodyObj)
  }
}

export default {
  init({commit}) {
    commit('init')
  },
  setZoom({commit}, {zoom}) {
    commit('setZoom', {zoom})
  },
  setCenter({commit}, {center}) {
    commit('setCenter', {center})
  },
  getLinks({commit}, {area}) {
    return fetch('/api/links', postOptions({area}))
      .then(res => res.json())
      .then(({links}) => commit('setLinks', {links}))
  },
  getWays({commit}, {area}) {
    return fetch('/api/ways', postOptions({area}))
      .then(res => res.json())
      .then(({ways}) => commit('setWays', {ways: ways}))
  },
  getNodes({commit}, {area}) {
    // return fetch('/api/nodes', postOptions({area}))
    //   .then(res => res.json())
    //   .then(({nodes}) => commit('setNodes', {nodes}))
    return fetch('/api/osm_nodes', postOptions({area}))
      .then(res => res.json())
      .then(({nodes}) => commit('setNodes', {nodes}))
  },
  getRoute({commit}, {start, end}) {
    const directionsService = new google.maps.DirectionsService()
    const request = {
      origin: start,
      destination: end,
      travelMode: 'DRIVING'
    }
    directionsService.route(request, (result, status) => {
      if (status == 'OK') {
        console.log(result)
      }
    })
  }
}
