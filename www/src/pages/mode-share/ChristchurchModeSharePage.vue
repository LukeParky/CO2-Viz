<template>
  <!-- The page that shows the map for the Christchurch area, comparing CO2 and VKT for each SA1 area -->
  <div class="full-height">
    <h1>ChCh mode share</h1>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import titleMixin from "@/mixins/title";

export default Vue.extend({
  name: "ChristchurchCo2Sa1Page",
  title: "Christchurch Map",
  mixins: [titleMixin],

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
