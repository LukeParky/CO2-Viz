<template>
  <main>
    <p>
      What if neighbourhoods were designed so that people could live sustainability with minimal effort? What can
      Aotearoa New Zealand learn from successful models both here and worldwide? To increase understanding of the
      relationship between urban form and emissions, this online mapping tool helps with visualisation of transport
      patterns and emissions. This tool is designed for a laptop or desktop machine, rather than a mobile device.
    </p>
    <h2>About the Visualisation</h2>
    <p>
      The tool itself currently has two key views: one is the emissions scenario visualisation; the other is the trends
      in travel mode. There are several tabs; Auckland, Christchurch, Wellington, and Oamaru which show the patterns for
      both emissions and transport in these places.
    </p>
    <h2>About the Emission Scenario Controller</h2>
    <p>
      The ‘emissions’ tab allows us to visualise how emissions change the overall flows of vehicles for each of the
      areas listed above. We can do this using the ‘Scenario Controller’. The baseline data is automatically loaded into
      the visualisation in the background map. Select any category to determine how shifts in the fuel type of vehicles
      will shift the CO2 footprint of the area of interest. We have kept the total vehicle kilometres travelled (VKT)
      constant for this scenario builder. In the example below we shift Hybrid to make up ¾ of the vehicle fleet and
      show that there would be a 44.91% reduction in total carbon emissions even with the same VKT.
    </p>
    <div>
      <!-- todo -->
    </div>
    <p>
      The visualisation can be controlled using the instructions in the screenshot below. Click on the ‘question mark’
      icon, see the icon here
      <span>
<!--        todo -->
      </span>
      to bring up the navigation instructions, which are shown below.
    </p>
    <div>
      <!--      todo -->
    </div>
    <h2>About the Mode Share Visualiser</h2>
    <p>
      <!--      todo trips to commutes -->
      The mode share tab visualises the transport patterns from the 2018 census for each of the cities and localities
      listed above. There are active transport (e.g. Walking and Cycling), public transport (e.g. bus), Drive, Passenger
      and other categories to select to help you understand the most recent travel trends in the region of interest. The
      data is focused on travel to work. There is a box in the top right-hand corner of the window to allow users to
      query the origin and destination data of where residents have come from and to work. Once an area is selected
      (e.g. Christchurch Central), it is possible to query Incoming, Outgoing or internal trips for that area. Selecting
      a particular area, by clicking on any of the circles, will display the trip data. For example, 6,825 incoming
      trips, 9 outgoing and 18 internal trips for Christchurch Central.
    </p>
    <p>
      Note: it is this data that has formed the basis of the ‘mode shift’ scenarios developed as part of the project.
    </p>
    <h2>About the Carbon Neutral Neighbourhood team</h2>
    <p>
      The Carbon Neutral Neighbourhood project is led by an interdisciplinary team at
      <span class="text-nowrap">Te Whare Wānanga o Waitaha |University of Canterbury.</span>
      The team has analysed international examples of well-functioning cities, towns and neighbourhoods that have low
      greenhouse gas (GHG) emissions. We have put all these case studies together into digestible reports. See link
      here:
      <a href="https://dx.doi.org/10.2139/ssrn.4410167">https://dx.doi.org/10.2139/ssrn.4410167</a>
      By providing accessible and actionable lessons, this knowledge will support planners to meet GHG emissions
      reduction goals. It aims to enable developing and retrofitting more sustainable, healthy, accessible, and
      resilient cities, towns and neighbourhoods across Aotearoa New Zealand.
    </p>
    <h2>Working Papers</h2>
    <p>
      Campbell M, Conrow L, Logan T, Kingham S <i>International Case Studies Report for in
      Greenhouse Gas Emissions Reductions: A Selected Portfolio of International Examples of Greenhouse Gas Emission
      Reduction Exemplars.</i> (October 31, 2022). Available at SSRN:
      <a href="https://ssrn.com/abstract=4410167">https://ssrn.com/abstract=4410167</a>
      or
      <a href="https://dx.doi.org/10.2139/ssrn.4410167">https://dx.doi.org/10.2139/ssrn.4410167</a>.
    </p>
    <p>And</p>
    <p>
      Campbell M, Conrow L, Logan T, Kingham S <i>Working paper: Lessons learned on how to
      design Aotearoa New Zealand’s urban centres to better enable low(er) carbon living.</i> (March 1, 2023).
      Available at SSRN: <a href="https://ssrn.com/abstract=4486347">https://ssrn.com/abstract=4486347</a> or
      <a href="https://dx.doi.org/10.2139/ssrn.4486347">https://dx.doi.org/10.2139/ssrn.4486347</a>.
    </p>
    <div class="row container-fluid">
      <div class="col-lg-12 col-md-12 col-xs-12 thumb">
        <a href="https://www.branz.co.nz/investing-research/building-research-levy/">
          <img class="img-fluid" src="/branz-logo.png" alt="BRANZ inc. logo">
        </a>
      </div>
      <div class="row container-fluid">
        <div class="col-lg-6 col-md-6 col-xs-6 thumb">
          <a href="https://canterbury.ac.nz">
            <img class="img-fluid" src="/UCRed_RGB.svg" alt="University of Canterbury logo">
          </a>
        </div>
        <div class="col-lg-6 col-md-6 col-xs-6 thumb">
          <a href="https://geospatial.ac.nz">
            <img class="img-fluid" src="/GRI_full_logo_transparent.png" alt="Geospatial Research Institute Logo">
          </a>
        </div>
      </div>
    </div>
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
