<template>
  <!-- Navigation Bar to allow switching between different pages in the app -->
  <div>
    <b-navbar type="light" variant="light">
      <b-navbar-toggle target="nav-text-collapse" />
      <b-navbar-brand :to="{name: 'Christchurch'}">
        Carbon Neutral Neighbourhoods
      </b-navbar-brand>
      <b-collapse id="nav-text-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item :to="{name: 'Auckland'}">
            Auckland
          </b-nav-item>
          <b-nav-item :to="{name: 'Wellington'}">
            Wellington
          </b-nav-item>
          <b-nav-item :to="{name: 'Christchurch'}">
            Christchurch
          </b-nav-item>
          <b-nav-item :to="{name: 'Oamaru'}">
            Oamaru
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  name: "TheNavBar"
})
</script>

<style scoped>

</style>
