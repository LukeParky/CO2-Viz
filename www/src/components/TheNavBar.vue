<template>
  <!-- Navigation Bar to allow switching between different pages in the app -->
  <div>
    <b-navbar type="light" variant="light">
      <b-navbar-brand :to="{name: routerLocations.Root.Root}">
        Carbon Neutral Neighbourhoods
      </b-navbar-brand>
      <b-collapse id="nav-text-collapse" is-nav>
        <b-navbar-nav>
          <template v-for="region of regions">
            <b-nav-item-dropdown :text="region">
              <b-dropdown-item>
                <b-nav-item :to="{name: routerLocations.Emissions[region]}">
                  Emissions
                </b-nav-item>
              </b-dropdown-item>
              <b-dropdown-item>
                <b-nav-item :to=" {name: routerLocations.ModeShare[region]}">
                  Mode Share
                </b-nav-item>
              </b-dropdown-item>
            </b-nav-item-dropdown>
          </template>
          <b-nav-item :to="{name: routerLocations.Root.About}">
            About
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
      <b-navbar-brand href="https://geospatial.ac.nz">
        <img
          src="GRI_no_subtitle_transparent.png"
          alt="Geospatial Research Institute Logo">
      </b-navbar-brand>
    </b-navbar>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import {RouterLocations} from "@/routes";

export default Vue.extend({
  name: "TheNavBar",
  data() {
    return {
      routerLocations: RouterLocations,
      regions: ["Auckland", "Wellington", "Christchurch", "Oamaru"]
    }
  }
})
</script>

<style scoped>
nav img {
  max-height: 30px;
}
</style>
