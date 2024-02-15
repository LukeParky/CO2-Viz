<template>
  <!-- The page that shows the map for the Christchurch area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <Co2Sa1Viewer
      :init-lat="christchurch.latitude"
      :init-long="christchurch.longitude"
      :urban-area-name="christchurch.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";

import Co2Sa1Viewer from "./Co2Sa1Viewer.vue";
import titleMixin from "@/mixins/title";

export default Vue.extend({
  name: "ChristchurchCo2Sa1Page",
  title: "Christchurch Map",
  mixins: [titleMixin],
  components: {
    Co2Sa1Viewer,
  },

  data() {
    return {
      christchurch: {
        latitude: -43.514137213246535,
        longitude: 172.62835098005368,
        urbanAreaName: "Christchurch"
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
