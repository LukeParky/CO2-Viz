<template>
  <!-- The page that shows the map for the Christchurch area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <ModeShareViewer
      :init-lat="wellington.latitude"
      :init-long="wellington.longitude"
      :urban-area-name="wellington.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import titleMixin from "@/mixins/title";
import ModeShareViewer from "./ModeShareViewer.vue"

export default Vue.extend({
  name: "WellingtonModeShareViewer",
  components: {ModeShareViewer},
  title: "Wellington Mode Shares",
  mixins: [titleMixin],

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

  beforeDestroy() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },
});
</script>

<style>
</style>
