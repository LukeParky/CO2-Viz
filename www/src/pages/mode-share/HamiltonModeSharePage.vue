<template>
  <!-- The page that shows the map for the Hamilton area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <ModeShareViewer
      :init-lat="hamilton.latitude"
      :init-long="hamilton.longitude"
      :urban-area-name="hamilton.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import titleMixin from "@/mixins/title";
import ModeShareViewer from "./ModeShareViewer.vue"

export default Vue.extend({
  name: "HamiltonCo2Sa1Page",
  components: {ModeShareViewer},
  title: "Hamilton Mode Shares",
  mixins: [titleMixin],

  data() {
    return {
      hamilton: {
        latitude: -37.786394,
        longitude: 175.277849,
        urbanAreaName: "Hamilton"
      },
      initHeight: 20000
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
