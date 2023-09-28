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
  async mounted() {
    // Limit scrolling on this page
    document.body.style.overflow = "hidden"

    this.dataSources = {geoJsonDataSources: [await this.loadSa1s()]};
    this.scenarios = [
      await this.loadCo2Emissions(),
      await this.loadVehicleKmTravelled()
    ];

  },
  beforeDestroy() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },
  methods: {
    async loadSa1s(): Promise<Cesium.GeoJsonDataSource> {
      return Cesium.GeoJsonDataSource.load("http://localhost:8080/sa1s-no-water.geojson", {
        fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 0.2),
        stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
        strokeWidth: 10

      });
    },

    async loadCo2Emissions(): Promise<Scenario> {
      const sa1s = await Cesium.GeoJsonDataSource.load("http://localhost:8080/sa1s-no-water.geojson");
      sa1s.show = false
      const colorScale = chroma.scale(['Teal', 'DarkRed'])
      const sa1Entities = sa1s.entities.values;
      for (const [i, entity] of sa1Entities.reverse().entries()) {
        const dataNum = (i % 50)
        const color = colorScale(dataNum / 50)
        const polyGraphics = new Cesium.PolygonGraphics({
          extrudedHeight: 10 * dataNum,
          material: new Cesium.Color(...color.gl()),
          outlineColor: new Cesium.Color(...color.darken().gl()),
        });
        polyGraphics.merge(entity.polygon)
        entity.polygon = polyGraphics;
      }

      return {name: "CO2 Emissions", geoJsonDataSources: [sa1s]};
    },

    async loadVehicleKmTravelled(): Promise<Scenario> {
      const sa1s = await Cesium.GeoJsonDataSource.load("http://localhost:8080/sa1s-no-water.geojson");
      sa1s.show = false;
      const colorScale = chroma.scale(['RoyalBlue', 'IndianRed'])
      const sa1Entities = sa1s.entities.values;
      for (const [i, entity] of sa1Entities.entries()) {
        const dataNum = (i % 50)
        const color = colorScale(dataNum / 50)
        const polyGraphics = new Cesium.PolygonGraphics({
          extrudedHeight: 10 * dataNum,
          material: new Cesium.Color(...color.gl()),
          outlineColor: new Cesium.Color(...color.darken().gl()),
        });
        polyGraphics.merge(entity.polygon)
        entity.polygon = polyGraphics;
      }
      return {name: "Vehicle Km Travelled", geoJsonDataSources: [sa1s]};
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
