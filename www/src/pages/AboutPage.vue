<template>
  <main>
    <p>
      What if neighbourhoods were designed so that people could live sustainability with minimal effort? What can
      Aotearoa New Zealand learn from successful models both here and worldwide?

      To increase understanding of the relationship between urban form and emissions, this online mapping tool helps
      with visualisation of transport and emissions. Led by an interdisciplinary team at
      <span class="text-nowrap">Te Whare Wānanga o Waitaha | University of Canterbury</span>, we’ve analysed
      international examples of well-functioning cities, towns and neighbourhoods that have low greenhouse gas (GHG)
      emissions. See link here: <a href="https://dx.doi.org/10.2139/ssrn.4410167">https://dx.doi.org/10.2139/ssrn.4410167</a>
      By providing accessible and actionable lessons, this knowledge will support planners to meet GHG emissions
      reduction goals. It aims to enable developing and retrofitting more sustainable, healthy, accessible and resilient
      cities, towns and neighbourhoods across Aotearoa New Zealand.
    </p>
    <div class="row container-fluid">
      <div class="col-lg-12 col-md-12 col-xs-12 thumb">
        <a href="https://www.branz.co.nz/investing-research/building-research-levy/">
          <img class="img-fluid" src="branz-logo.png" alt="BRANZ inc. logo">
        </a>
      </div>
      <div class="row container-fluid">
        <div class="col-lg-6 col-md-6 col-xs-6 thumb">
          <a href="https://canterbury.ac.nz">
            <img class="img-fluid" src="UCRed_RGB.svg" alt="University of Canterbury logo">
          </a>
        </div>
        <div class="col-lg-6 col-md-6 col-xs-6 thumb">
          <a href="https://geospatial.ac.nz">
            <img class="img-fluid" src="GRI_full_logo_transparent.png" alt="Geospatial Research Institute Logo">
          </a>
        </div>
      </div>
    </div>
    <h2>Working Papers</h2>
    <p>
      Campbell, Malcolm and Conrow, Lindsey and Logan, Tom and Kingham, Simon, <i>International Case Studies Report for in
      Greenhouse Gas Emissions Reductions: A Selected Portfolio of International Examples of Greenhouse Gas Emission
      Reduction Exemplars.</i> (October 31, 2022). Available at SSRN:
      <a href="https://ssrn.com/abstract=4410167">https://ssrn.com/abstract=4410167</a>
      or
      <a href="https://dx.doi.org/10.2139/ssrn.4410167">https://dx.doi.org/10.2139/ssrn.4410167</a>.
    </p>
    <p>And</p>
    <p>
      Campbell, Malcolm and Conrow, Lindsey and Kingham, Simon and Logan, Tom, <i>Working paper: Lessons learned on how to
      design Aotearoa New Zealand’s urban centres to better enable low(er) carbon living.</i> (March 1, 2023). Available at
      SSRN: <a href="https://ssrn.com/abstract=4486347">https://ssrn.com/abstract=4486347</a> or <a
      href="https://dx.doi.org/10.2139/ssrn.4486347">https://dx.doi.org/10.2139/ssrn.4486347</a>.
    </p>
  </main>
</template>

<script lang="ts">
import Vue from "vue";

import titleMixin from "@/mixins/title";

export default Vue.extend({
  name: "AboutPage",
  title: "About",
  mixins: [titleMixin],

});
</script>

<style>
.img-fluid {
  padding: 20px
}
h2 {
  padding-top: 15px;
}
</style>
