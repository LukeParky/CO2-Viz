<template>
  <!-- The page that shows the map for the Digital Twin -->
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
import Vue from "vue";

import Co2Sa1Viewer from "@/components/Co2Sa1Viewer.vue";
import titleMixin from "@/mixins/title";

export default Vue.extend({
  name: "AucklandCo2Sa1Page",
  title: "Auckland Map",
  mixins: [titleMixin],
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

  beforeDestroy() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },
});
</script>

<style>
</style>
