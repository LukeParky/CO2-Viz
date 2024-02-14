<template>
<!-- The page that shows the map for the Oamaru area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <Co2Sa1Viewer
      :init-lat="oamaru.latitude"
      :init-long="oamaru.longitude"
      :urban-area-name="oamaru.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";

import Co2Sa1Viewer from "@/components/Co2Sa1Viewer.vue";
import titleMixin from "@/mixins/title";

export default Vue.extend({
  name: "OamaruCo2Sa1Page",
  title: "Oamaru Map",
  mixins: [titleMixin],
  components: {
    Co2Sa1Viewer,
  },

  data() {
    return {
      oamaru: {
        latitude: -45.09652014809901,
        longitude: 170.9714064482898,
        urbanAreaName: "oamaru"
      },
      initHeight: 15000
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
