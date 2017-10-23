
export default {
  zoom: state => state.zoom,
  center: state => ({lat: state.lat, lng: state.lng}),
  links: state => state.links,
  ways: state => state.ways,
  nodes: state => state.nodes
}
