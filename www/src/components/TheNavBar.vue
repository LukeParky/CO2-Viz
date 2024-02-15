<template>
  <!-- Navigation Bar to allow switching between different pages in the app -->
  <div>
    <b-navbar type="light" variant="light">
      <b-navbar-toggle target="nav-text-collapse" />
      <b-navbar-brand :to="{name: routerLocations.RootPage}">
        Carbon Neutral Neighbourhoods
      </b-navbar-brand>
      <b-collapse id="nav-text-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item :to="{name: routerLocations.AucklandCo2Sa1Page}">
            Auckland
          </b-nav-item>
          <b-nav-item :to="{name: routerLocations.WellingtonCo2Sa1Page}">
            Wellington
          </b-nav-item>
          <b-nav-item-dropdown text="Christchurch">
            <b-nav-item :to="{name: routerLocations.ChristchurchCo2Sa1Page}">
              Emissions
            </b-nav-item>
            <b-nav-item :to="{name: routerLocations.ChristchurchModeSharePage}">
              Mode Share
            </b-nav-item>
          </b-nav-item-dropdown>
          <b-nav-item :to="{name: routerLocations.OamaruCo2Sa1Page}">
            Oamaru
          </b-nav-item>
          <b-nav-item :to="{name: routerLocations.AboutPage}">
            About
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import {routerLocations} from "@/routes";

export default Vue.extend({
  name: "TheNavBar",
  data() {
    return {
      routerLocations
    }
  }
})
</script>

<style scoped>

</style>
