<template>
  <!-- Navigation Bar to allow switching between different pages in the app -->
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <router-link class="navbar-brand" :to="{name: routerLocations.Root.Root}">
        Carbon Neutral Neighbourhoods
      </router-link>

      <button class="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarText"
              aria-controls="navbarText"
              aria-expanded="false"
              aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarText">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li v-for="region of regions"
              :key="region.key"
              class="nav-item dropdown"
          >
            <a class="nav-link"
               href="#"
               :id="`navbarDropdown${region.key}`"
               role="button"
               data-bs-toggle="dropdown"
               aria-expanded="false"
            >
              {{ region.display }}
            </a>
            <ul class="dropdown-menu" :aria-labelledby="`navbarDropdown${region.key}`">
              <li class="dropdown-item">
                <router-link :to="{name: routerLocations.Emissions[region.key]}">
                  Emissions
                </router-link>
              </li>
              <li class="dropdown-item">
                <router-link :to="{name: routerLocations.ModeShare[region.key]}">
                  Mode Share
                </router-link>
              </li>
            </ul>
          </li>
          <li class="nav-item">
            <router-link :to="{name: routerLocations.Root.About}">
              Find out more | Kimihia te roanga atu
            </router-link>
          </li>
        </ul>
      </div>
      <a class="navbar-brand" href="https://geospatial.ac.nz">
        <img
          src="/GRI_no_subtitle_transparent.png"
          alt="Geospatial Research Institute Logo">
      </a>
    </div>
  </nav>
</template>

<script lang="ts">
import {defineComponent} from "vue";
import {RouterLocations} from "@/routes";

export default defineComponent({
  name: "TheNavBar",
  data() {
    return {
      routerLocations: RouterLocations as {
        Emissions: {
          [location: string]: string
        },
        ModeShare: {
          [location: string]: string
        },
        Root: {
          [location: string]: string
        },
      },
      regions: [
        {display: "Auckland | Tāmaki Makaurau", key: "Auckland"},
        {display: "Hamilton | Kirikiriroa", key: "Hamilton"},
        {display: "Wellington | Te Whanganui-a-Tara", key: "Wellington"},
        {display: "Christchurch | Ōtautahi", key: "Christchurch"},
        {display: "Oamaru | Oāmaru", key: "Oamaru"},
        {display: "Queenstown | Tāhuna", key: "Queenstown"},
      ]
    }
  }
})
</script>

<style scoped>
nav img {
  max-height: 30px;
}
</style>
