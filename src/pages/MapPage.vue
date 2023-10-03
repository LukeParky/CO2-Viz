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
    <div id="filter-form" class="card">
      <h2 class="card-title">
        Filters
      </h2>
      <div>{{ selectedVehicleClass }} | {{ selectedFuelType }}</div>
      <div class="form-group">
        <h3>Vehicle Class:</h3>
        <div class="form-check" v-for="vehicleClass of vehicleClasses" :key="toKebabCase(vehicleClass)">
          <input
            type="radio"
            :id="toKebabCase(vehicleClass)"
            :value="toKebabCase(vehicleClass)"
            v-model="selectedVehicleClass"
          >
          <label :for="toKebabCase(vehicleClass)">{{ vehicleClass }}</label>
        </div>
      </div>
      <div class="form-group">
        <h3>Vehicle Fuel Type:</h3>
        <div class="form-check" v-for="fuelType of fuelTypes" :key="toKebabCase(fuelType)">
          <input
            type="radio"
            :id="toKebabCase(fuelType)"
            :value="toKebabCase(fuelType)"
            v-model="selectedFuelType"
          >
          <label :for="toKebabCase(fuelType)">{{ fuelType }}</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import * as Cesium from "cesium";
import chroma, {Scale} from "chroma-js";
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
      dataSources: {geoJsonDataSources: []} as MapViewerDataSourceOptions,
      scenarios: [] as Scenario[],
      cesiumApiToken: process.env.VUE_APP_CESIUM_ACCESS_TOKEN,
      vehicleClasses: ["All Vehicle Classes", "Cars", "Light Vehicles", "Busses"],
      fuelTypes: ["All Fuel Types", "Petrol", "Diesel", "Hybrid", "Plug-in Hybrid", "Electric"],
      selectedVehicleClass: "",
      selectedFuelType: "",
    }
  },

  created() {
    this.selectedVehicleClass = this.toKebabCase(this.vehicleClasses[0])
    this.selectedFuelType = this.toKebabCase(this.fuelTypes[0])
  },

  async mounted() {
    // Limit scrolling on this page
    document.body.style.overflow = "hidden"

    this.loadSa1s().then((geojson) => {
      if (this.dataSources.geoJsonDataSources == undefined) {
        this.dataSources.geoJsonDataSources = [geojson]
      } else {
        this.dataSources.geoJsonDataSources?.push(geojson)
      }
    })

    this.loadCo2Emissions().then((geoJson) => {
      this.scenarios.push(geoJson)
    })
  },
  beforeDestroy() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },
  methods: {
    toKebabCase(str: string): string {
      return str.split(" ").join("-").toLowerCase()
    },
    async loadSa1s(): Promise<Cesium.GeoJsonDataSource> {
      return Cesium.GeoJsonDataSource.load("http://localhost:8080/sa1s_in_chch.geojson", {
        fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 0.2),
        stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
        strokeWidth: 10

      });
    },

    async loadCo2Emissions(): Promise<Scenario> {
      const sa1s = await Cesium.GeoJsonDataSource.load("http://localhost:8080/sa1s_with_data.geojson");
      sa1s.show = false
      const colorScale = chroma.scale(chroma.brewer.Viridis)
      const sa1Entities = sa1s.entities.values;
      for (const entity of sa1Entities.reverse()) {
        if (entity.polygon != null) {
          const co2 = entity.properties["CO2 (Tonnes/Year)"].getValue()
          const vkt = entity.properties["VKT (`000,000 km/Year)"].getValue()
          const color = colorScale(vkt / 70)
          const polyGraphics = new Cesium.PolygonGraphics({
            extrudedHeight: co2 / 5,
            material: new Cesium.Color(...color.gl()),
            outlineColor: new Cesium.Color(...color.darken().gl()),
          });
          polyGraphics.merge(entity.polygon)
          entity.polygon = polyGraphics;
        }
      }

      return {name: "CO2 Emissions", geoJsonDataSources: [sa1s]};
    },

    async loadVehicleKmTravelled(): Promise<Scenario> {
      const sa1s = await Cesium.GeoJsonDataSource.load("http://localhost:8080/sa1s_with_data.geojson");
      sa1s.show = false;
      const colorScale = chroma.scale(chroma.brewer.Viridis)
      const sa1Entities = sa1s.entities.values;
      for (const [i, entity] of sa1Entities.entries()) {
        if (entity.polygon != null) {
          // console.log(entity)
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

#filter-form {
  position: absolute;
  bottom: 40px;
  right: 30px;
}
</style>
