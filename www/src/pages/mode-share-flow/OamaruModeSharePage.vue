<template>
  <!-- The page that shows the map for the Oamaru area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <ModeShareViewer
      :init-lat="oamaru.latitude"
      :init-long="oamaru.longitude"
      :urban-area-name="oamaru.urbanAreaName"
      :init-height="initHeight"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import titleMixin from "@/mixins/title";
import ModeShareViewer from "./ModeShareViewer.vue"

export default Vue.extend({
  name: "OamaruCo2Sa1Page",
  components: {ModeShareViewer},
  title: "Oamaru Mode Shares",
  mixins: [titleMixin],

  data() {
    return {
      oamaru: {
        latitude: -43.514137213246535,
        longitude: 172.62835098005368,
        urbanAreaName: "Oamaru"
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
