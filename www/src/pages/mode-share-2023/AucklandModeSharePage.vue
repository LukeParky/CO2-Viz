<template>
  <!-- The page that shows the map for the Christchurch area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <ModeShareViewer
      :init-lat="auckland.latitude"
      :init-long="auckland.longitude"
      :urban-area-name="auckland.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import titleMixin from "@/mixins/title";
import ModeShareViewer from "./ModeShareViewer.vue"

export default Vue.extend({
  name: "AucklandModeShareViewer",
  components: {ModeShareViewer},
  title: "Auckland Mode Shares",
  mixins: [titleMixin],

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
