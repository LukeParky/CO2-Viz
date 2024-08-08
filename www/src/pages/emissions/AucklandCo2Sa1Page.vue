<template>
  <!-- The page that shows the map for the Auckland area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <Co2Sa1Viewer
      :init-lat="auckland.latitude"
      :init-long="auckland.longitude"
      :urban-area-name="auckland.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import {defineComponent} from "vue";

import Co2Sa1Viewer from "./Co2Sa1Viewer.vue";

export default defineComponent({
  name: "AucklandCo2Sa1Page",
  components: {
    Co2Sa1Viewer,
  },

  data() {
    return {
      auckland: {
        latitude: -36.859963793734856,
        longitude: 174.7609620989333,
        urbanAreaName: "Auckland"
      },
      initHeight: 25000
    }
  },
  async mounted() {
    // Limit scrolling on this page
    document.body.style.overflow = "hidden"
  },

  beforeUnmount() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },
});
</script>

<style>
</style>
