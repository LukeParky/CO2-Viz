<template>
  <!-- The page that shows the map for the Digital Twin -->
  <div class="full-height">
    <Co2Sa1Viewer
      :init-lat="wellington.latitude"
      :init-long="wellington.longitude"
      :urban-area-name="wellington.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import {defineComponent} from "vue";

import Co2Sa1Viewer from "./Co2Sa1Viewer.vue";

export default defineComponent({
  name: "WellingtonCo2Sa1Page",
  components: {
    Co2Sa1Viewer,
  },

  data() {
    return {
      wellington: {
        latitude: -41.29187960932575,
        longitude: 174.7782747022341,
        urbanAreaName: "Wellington"
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
