<template>
  <div>
    <GmapMap style="width: 100%; height: 1000px;" :zoom="zoom" :center="center" ref="map"
      @center_changed="centerChanged" @zoom_changed="zoomChanged" @bounds_changed="boundsChanged">
      <GmapPolyline v-for="link in links" :key="link.$index" :path="link.coordinates" :options="{strokeColor: link.strokeColor}"
        @mouseover="lineMouseOver(link, $event)"/>
      <GmapPolyline v-for="way in ways" :key="way.$index" :path="way.coordinates" :options="{strokeColor: way.strokeColor}"
        @mouseover="lineMouseOver(way, $event)"/>
      <!-- <GmapMarker v-for="node in nodes" :key="node.$index" :position="node"
        @mouseover="markerMouseOver(node, $event)"/> -->
    </GmapMap>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { debounce } from 'lodash'
import ColorHash from 'color-hash'

const colorHash = new ColorHash({lightness: 0.5})

export default {
  computed: {
    ...mapGetters([
      'zoom',
      'center',
      // 'links',
      'nodes'
    ]),
    links () {
      if (this.$store.state.links)
        // return this.$store.state.links.map(link => Object.assign(link, {strokeColor: colorHash.hex(link.id)}))
        return this.$store.state.links.map(link => Object.assign(link, {strokeColor: 'red'}))
      else
        return null
    },
    ways () {
      if (this.$store.state.ways)
        // return this.$store.state.ways.map(way => Object.assign(way, {strokeColor: colorHash.hex(way.id)}))
        return this.$store.state.ways.map(way => Object.assign(way, {strokeColor: colorHash.hex(way.highway)}))
        // return this.$store.state.ways.map(way => Object.assign(way, {strokeColor: 'green'}))
      else
        return null
    },
    nodes () {
      if (this.$store.state.ways)
        return this.$store.state.ways.map(way => way.coordinates).reduce((a, b) => a.concat(b), [])
      else
        return null
    }
  },
  methods: {
    lineMouseOver (link, e) {
      console.log('lineMouseOver', 'id', link.id, 'highway', link.highway, 'start', link.coordinates[0].lat, link.coordinates[0].lng, 'end', link.coordinates[1].lat, link.coordinates[1].lng)
    },
    markerMouseOver (node, e) {
      console.log('markerMouseOver', 'pos', node.coordinates.lat, node.coordinates.lng)
    },
    boundsChanged: debounce(function (e) {
      this.$store.dispatch('getLinks', {area: {type: 'Polygon', coordinates: [[[e.b.b, e.f.f], [e.b.f, e.f.f], [e.b.f, e.f.b], [e.b.b, e.f.b], [e.b.b, e.f.f]]]}})
      this.$store.dispatch('getWays', {area: {type: 'Polygon', coordinates: [[[e.b.b, e.f.f], [e.b.f, e.f.f], [e.b.f, e.f.b], [e.b.b, e.f.b], [e.b.b, e.f.f]]]}})
      // this.$store.dispatch('getNodes', {area: {type: 'Polygon', coordinates: [[[e.b.b, e.f.f], [e.b.f, e.f.f], [e.b.f, e.f.b], [e.b.b, e.f.b], [e.b.b, e.f.f]]]}})
    }, 1000),
    zoomChanged: debounce(function (zoom) {
      this.$store.dispatch('setZoom', {zoom})
    }, 300),
    centerChanged: debounce(function (center) {
      const lat = center.lat()
      const lng = center.lng()
      const epsilon = 10e-6
      if (Math.abs(this.center.lat - lat) > epsilon || Math.abs(this.center.lng - lng) > epsilon) {
        this.$store.dispatch('setCenter', {center: {lat, lng}})
      }
    }, 300),
  }
}
</script>
