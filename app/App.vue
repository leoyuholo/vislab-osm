<template>
  <div>
    <GmapMap style="width: 100%; height: 1000px;" :zoom="zoom" :center="center" ref="map" @center_changed="centerChanged" @zoom_changed="zoomChanged" @tilesloaded="tilesloaded">
      <GmapPolyline v-for="link in links" :key="link.id" :path="link.coordinates" :options="{strokeColor: 'red'}"/>
    </GmapMap>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { debounce } from 'lodash'
export default {
  computed: {
    ...mapGetters([
      'zoom',
      'center',
      'links'
    ])
  },
  methods: {
    tilesloaded () {
      this.$store.dispatch('getLinks', {area: {type: 'polygon', coordinates: [[], [], [], []]}})
    },
    zoomChanged: debounce(function (zoom) {
      this.$store.dispatch('setZoom', {zoom})
    }, 300),
    centerChanged: debounce(function (center) {
      this.$store.dispatch('setCenter', {center: {lat: center.lat(), lng: center.lng()}})
    }, 300),
  }
}
</script>
