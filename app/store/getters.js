
export default {
  zoom: state => state.zoom,
  center: state => ({lat: state.lat, lng: state.lng}),
  links: state => state.links,
  nodes: state => state.nodes
}
