<template>
  <!-- Navigation Bar to allow switching between different pages in the app -->
  <div>
    <b-navbar type="light" variant="light">
      <b-navbar-toggle target="nav-text-collapse" />
      <b-navbar-brand :to="{name: routerLocations.Root.Root}">
        Carbon Neutral Neighbourhoods
      </b-navbar-brand>
      <b-collapse id="nav-text-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item :to="{name: routerLocations.Emissions.Auckland}">
            Auckland
          </b-nav-item>
          <b-nav-item :to="{name: routerLocations.Emissions.Wellington}">
            Wellington
          </b-nav-item>
          <b-nav-item-dropdown text="Christchurch">
            <b-nav-item :to="{name: routerLocations.Emissions.Christchurch}">
              Emissions
            </b-nav-item>
            <b-nav-item :to="{name: routerLocations.ModeShare.Christchurch}">
              Mode Share
            </b-nav-item>
          </b-nav-item-dropdown>
          <b-nav-item :to="{name: routerLocations.Emissions.Oamaru}">
            Oamaru
          </b-nav-item>
          <b-nav-item :to="{name: routerLocations.Root.About}">
            About
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
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
      routerLocations: RouterLocations
    }
  }
})
</script>

<style scoped>

</style>
