<template>
  <!-- The page that shows the map for the Queenstown area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <Co2Sa1Viewer
      :init-lat="queenstown.latitude"
      :init-long="queenstown.longitude"
      :urban-area-name="queenstown.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import {defineComponent} from "vue";

import Co2Sa1Viewer from "./Co2Sa1Viewer.vue";

export default defineComponent({
  name: "QueenstownCo2Sa1Page",
  components: {
    Co2Sa1Viewer,
  },

  data() {
    return {
      queenstown: {
        latitude: -45.02965,
        longitude: 168.70099,
        urbanAreaName: "Queenstown"
      },
      initHeight: 20000
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
