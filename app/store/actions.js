
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
  getNodes({commit}, {area}) {
    return fetch('/api/nodes', postOptions({area}))
      .then(res => res.json())
      .then(({nodes}) => commit('setNodes', {nodes}))
  }
}
