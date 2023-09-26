<template>
  <!-- The page that shows the map for the Digital Twin -->
  <div class="full-height">
    <MapViewer
      :init-lat="christchurch.latitude"
      :init-long="christchurch.longitude"
      :init-height="20000"
      :cesium-access-token="cesiumApiToken"
      :data-sources="dataSources"
      :scenarios="scenarios"
    />
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components/src/components';
import titleMixin from "@/mixins/title";
import {MapViewerDataSourceOptions, Scenario} from "geo-visualisation-components/dist/types/src/types";

export default Vue.extend({
  name: "MapPage",
  title: "Map",
  mixins: [titleMixin],
  components: {
    MapViewer,
  },
  data() {
    return {
      christchurch: {
        latitude: -43.514137213246535,
        longitude: 172.62835098005368
      },
      dataSources: {} as MapViewerDataSourceOptions,
      scenarios: [] as Scenario[],
      cesiumApiToken: process.env.VUE_APP_CESIUM_ACCESS_TOKEN,
    }
  },
  mounted() {
    // Limit scrolling on this page
    document.body.style.overflow = "hidden"

    this.loadVehicleKmTravelled("http://localhost:8080/sa1s-no-water.geojson").then((sa1s) => {
      this.dataSources = {geoJsonDataSources: [sa1s]};
      console.log("added sa1s")
    });
  },
  beforeDestroy() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },
  methods: {
    async loadVehicleKmTravelled(url: string): Promise<Cesium.GeoJsonDataSource> {
      const sa1s = await Cesium.GeoJsonDataSource.load(url);
      const colorScale = chroma.scale(['RoyalBlue', 'IndianRed'])
      const sa1Entities = sa1s.entities.values;
      for (const [i, entity] of sa1Entities.entries()) {
        const dataNum = (i % 50)
        const color = colorScale(dataNum / 50)
        const polyGraphics = new Cesium.PolygonGraphics({
          extrudedHeight: 10 * dataNum,
          material: new Cesium.Color(...color.gl()),
          outlineColor: new Cesium.Color(...color.brighten().gl()),
        });
        polyGraphics.merge(entity.polygon)
        entity.polygon = polyGraphics;
      }

      return sa1s;
    },
  },
  computed: {
    scenarioNames(): Array<string> {
      return this.scenarios.map(scenario => scenario.name);
    }
  }
});
</script>

<style>
#legend {
  position: absolute;
  bottom: 40px;
  right: 30px;
  height: 175px
}
</style>
