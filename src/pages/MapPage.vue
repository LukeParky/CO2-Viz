<template>
  <!-- The page that shows the map for the Digital Twin -->
  <div class="full-height">
    <BalancedSlider
      v-if="sliderDefaultValues.length > 0"
      :init-values="sliderDefaultValues"
      @submit="changeUseRates($event)"
      :disabled="selectedFuelType !== 'all'"
    />
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
      <div>{{ selectedFuelType }}</div>
      <div class="form-group">
        <h3>Car Fuel Type:</h3>
        <div class="form-check" v-for="fuelType of fuelTypes" :key="fuelType.key">
          <input
            type="radio"
            :id="fuelType.key"
            :value="fuelType.key"
            v-model="selectedFuelType"
          >
          <label :for="fuelType.key">{{ fuelType.display }}</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components/src/components';
import titleMixin from "@/mixins/title";
import {MapViewerDataSourceOptions, Scenario} from "geo-visualisation-components/dist/types/src/types";
import axios from "axios";
import BalancedSlider from "@/components/BalancedSlider.vue";

export default Vue.extend({
  name: "MapPage",
  title: "Map",
  mixins: [titleMixin],
  components: {
    BalancedSlider,
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
      vehicleClasses: [{
        display: "All Vehicle Classes",
        key: "all"
      }, {
        display: "Cars",
        key: "car"
      }, {
        display: "Light Vehicles",
        key: "light"
      }, {
        display: "Busses",
        key: "bus"
      }
      ],
      fuelTypes: [{
        display: "All Fuel Types",
        key: "all"
      }, {
        display: "Petrol",
        key: "petrol"
      }, {
        display: "Diesel",
        key: "diesel"
      }
      ],
      vktUseRates: [] as {fuel_type: string, VKT: number, weight: number}[],
      sliderDefaultValues: [] as {name: string, value: number}[],
      selectedVehicleClass: "",
      selectedFuelType: "",
    }
  },

  created() {
    this.selectedVehicleClass = this.vehicleClasses[1].key
    this.selectedFuelType = this.fuelTypes[1].key
  },

  async mounted() {
    // Limit scrolling on this page
    document.body.style.overflow = "hidden"

    const geojson = await this.loadSa1s()
    this.dataSources.geoJsonDataSources = [geojson]

    this.vktUseRates = await this.fetchVktSums();
    console.log(this.vktUseRates)
    this.sliderDefaultValues = this.vktUseRates.map(obj => ({name: obj.fuel_type, value: obj.weight}))
    await this.styleSa1s(geojson);

  },

  beforeDestroy() {
    // Reset scrolling for other pages
    document.body.style.overflow = ""
  },

  watch: {
    selectedFuelType() {
      this.styleSa1s()
    },

  },

  methods: {
    toKebabCase(str: string): string {
      return str.split(" ").join("-").toLowerCase()
    },
    async loadSa1s(): Promise<Cesium.GeoJsonDataSource> {
      const geoserverUrl = `http://localhost:8087/geoserver/carbon_neutral/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=carbon_neutral%3Asa1s&outputFormat=application%2Fjson`
      const sa1s = await Cesium.GeoJsonDataSource.load(geoserverUrl, {
        fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 0.2),
        stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
        strokeWidth: 10
      });
      return sa1s;
    },

    async fetchVktSums(): Promise<{fuel_type: string, VKT: number, weight: number}[]>{
      const propertyRequestUrl = `http://localhost:8087/geoserver/carbon_neutral/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=carbon_neutral%3Avkt_sum&outputFormat=application%2Fjson&propertyname=(fuel_type,VKT)`
      const propertyJson = await axios.get(propertyRequestUrl)
      const features = propertyJson.data.features as {properties: {fuel_type: string, VKT: number}}[]

      const fuel_to_vkts =  features.map(feature => feature.properties)
      const total_vkt = fuel_to_vkts.reduce((partialSum, entry) => partialSum + entry.VKT, 0)
      return fuel_to_vkts.map(entry => ({...entry, weight: entry.VKT / total_vkt * 100}))
    },

    changeUseRates(changeEvent: number[]) {
      for (const i in changeEvent) {
        this.vktUseRates[i].weight = changeEvent[i]
      }
      this.styleSa1s()
    },


    async styleSa1s(): Promise<void> {
      const geoJsons = this.dataSources.geoJsonDataSources;
      if (geoJsons == undefined || geoJsons.length > 0) {
        return
      }
      const sa1s = geoJsons[0]

      const sqlView = this.selectedFuelType === "all" ? "all_cars" : "fuel_type";
      const propertyRequestUrl = `http://localhost:8087/geoserver/carbon_neutral/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=carbon_neutral%3Asa1_emissions_${sqlView}&viewparams=FUEL_TYPE:${this.selectedFuelType}&outputFormat=application%2Fjson&propertyname=(SA12018_V1_00,CO2,VKT,AREA_SQ_KM)`
      const propertyJson = await axios.get(propertyRequestUrl)
      const emissionsData = propertyJson.data.features

      const colorScale = chroma.scale(chroma.brewer.Viridis)
      const sa1Entities = sa1s.entities.values;
      const sa1IdColumnName = "SA12018_V1_00"
      for (const entity of sa1Entities.reverse()) {
        if (entity.polygon != null) {
          const entityData = emissionsData.find((emissionReading) => emissionReading.properties[sa1IdColumnName] == entity.properties[sa1IdColumnName]?.getValue())
          let polyGraphics: Cesium.PolygonGraphics
          if (entityData == undefined) {
            polyGraphics = new Cesium.PolygonGraphics({show: false})
          } else {
            const area = entityData.properties["AREA_SQ_KM"]
            const co2 = entityData.properties["CO2"]
            const vkt = entityData.properties["VKT"]
            const color = colorScale(vkt / area / 100000)
            polyGraphics = new Cesium.PolygonGraphics({
              show: true,
              extrudedHeight: co2 / (area * 10),
              material: new Cesium.Color(...color.gl()),
              outlineColor: new Cesium.Color(...color.darken().gl()),
            });
          }
          polyGraphics.merge(entity.polygon)
          entity.polygon = polyGraphics;
        }
      }
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
    },
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
  bottom: 0px;
  right: 30px;
}
</style>
