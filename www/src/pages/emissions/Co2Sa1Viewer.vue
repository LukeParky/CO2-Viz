<template>
  <!-- The component that renders a CO2/VKT map for a given area of SA1s -->
  <div class="full-height">
    <MapViewer
      :init-lat="initLat"
      :init-long="initLong"
      :init-height="initHeight"
      :init-base-layer="baseLayer"
      :cesium-access-token="cesiumApiToken"
      :data-sources="dataSources"
    />
    <div
      id="control-card"
      class="card"
    >
      <p>
        Total CO2:
        <span class="value">{{ formattedTotals.CO2 }}</span>
      </p>
      <p>
        Total Vehicle Km Travelled:
        <span class="value">{{ formattedTotals.VKT }}</span>
      </p>
      <BalancedSlider
        v-if="sliderDefaultValues.length > 0"
        :init-values="sliderDefaultValues"
        @submit="changeUseRates($event)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components/src/components';
import {MapViewerDataSourceOptions} from "geo-visualisation-components/src/types";
import Vue from "vue";

import BalancedSlider from "@/components/BalancedSlider.vue";
import {roundToFixed} from "@/utils";

interface Sa1Emissions {
  SA12018_V1_00: number,
  AREA_SQ_KM: number,
  CO2?: number,
  VKT: number,

  [k: `CO2_${string}`]: number | undefined,
}


export default Vue.extend({
  name: "Co2Sa1Viewer",
  components: {
    BalancedSlider,
    MapViewer,
  },

  props: {
    /** Initial latitude for map view */
    initLat: {
      type: Number,
      required: true,
      validator: (value: number) => -90 <= value && value <= 90,
    },
    /** Initial longitude for map view */
    initLong: {
      type: Number,
      required: true,
      validator: (value: number) => -180 <= value && value <= 180,
    },
    /** Urban area name for filtering areas, given from the StatsNZ Urban Rural dataset, UR2023_V1_00_NAME */
    urbanAreaName: {
      type: String,
      required: true
    },
    /** Initial height of the camera in metres. Default is 2000m */
    initHeight: {
      type: Number,
      default: 2000,
    },
  },

  data() {
    return {
      baseLayer: new Cesium.ImageryLayer(new Cesium.OpenStreetMapImageryProvider({}), {}),
      geoserverHost: `${process.env.VUE_APP_GEOSERVER_HOST}:${process.env.VUE_APP_GEOSERVER_PORT}`,
      dataSources: {geoJsonDataSources: []} as MapViewerDataSourceOptions,
      cesiumApiToken: process.env.VUE_APP_CESIUM_ACCESS_TOKEN,
      vktUseRates: [] as { fuel_type: string, VKT: number, CO2: number, weight: number }[],
      sliderDefaultValues: [] as { name: string, value: number }[],
    }
  },

  async created() {
    this.vktUseRates = await this.fetchVktSums();
    this.sliderDefaultValues = this.vktUseRates.map(obj => ({name: obj.fuel_type, value: obj.weight}))
  },

  async mounted() {
    const geojson = await this.loadSa1s()
    this.dataSources.geoJsonDataSources = [geojson]

    await this.styleSa1s();

  },

  methods: {
    async loadSa1s(): Promise<Cesium.GeoJsonDataSource> {
      const geoserverUrl = axios.getUri({
        url: `${this.geoserverHost}/geoserver/sa1_emissions/ows`,
        params: {
          service: "WFS",
          version: "1.0.0",
          request: "GetFeature",
          outputFormat: "application/json",
          typeName: "sa1_emissions:sa1s",
          cql_filter: `UR2023_V1_00_NAME ILIKE '${this.urbanAreaName}'`
        }
      })

      const sa1s = await Cesium.GeoJsonDataSource.load(geoserverUrl, {
        fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 1),
        stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
        strokeWidth: 10
      });
      return sa1s;
    },

    async fetchVktSums(): Promise<{ fuel_type: string, VKT: number, CO2: number, weight: number }[]> {
      const propertyRequestUrl = axios.getUri({
        url: `${this.geoserverHost}/geoserver/sa1_emissions/ows`,
        params: {
          service: "WFS",
          version: "1.0.0",
          request: "GetFeature",
          outputFormat: "application/json",
          typeName: "sa1_emissions:vkt_sum",
          propertyname: "(fuel_type,VKT,CO2)",
          cql_filter: `UR2023_V1_00_NAME ILIKE '${this.urbanAreaName}'`
        }
      })
      const propertyJson = await axios.get(propertyRequestUrl)
      const features = propertyJson.data.features as { properties: { fuel_type: string, VKT: number, CO2: number } }[]

      const fuel_to_vkts = features.map(feature => feature.properties)
      const total_vkt = fuel_to_vkts.reduce((partialSum, entry) => partialSum + entry.VKT, 0)
      return fuel_to_vkts.map(entry => ({...entry, weight: entry.VKT / total_vkt * 100}))
    },

    changeUseRates(changeEvent: number[]) {
      for (const i in changeEvent) {
        this.vktUseRates[i].weight = changeEvent[i]
      }
      this.styleSa1s()
    },

    getStyleInputVariables(sa1: Sa1Emissions): { area_sq_km: number, vkt: number, co2: number } {
      let co2 = sa1.CO2;
      if (co2 === undefined) {
        co2 = 0;
        for (const {fuel_type, weight} of this.vktUseRates) {
          const defaultWeight = this.sliderDefaultValues.find((defVal) => defVal.name === fuel_type)?.value;
          const sa1FuelCo2Contribution = sa1[`CO2_${fuel_type}`]
          if (defaultWeight !== undefined && sa1FuelCo2Contribution !== undefined) {
            co2 += (weight / defaultWeight) * sa1FuelCo2Contribution
          }
        }
      }
      return {area_sq_km: sa1.AREA_SQ_KM, vkt: sa1.VKT, co2}
    },

    async styleSa1s(): Promise<void> {
      console.log("Loading started")
      const geoJsons = this.dataSources.geoJsonDataSources;
      if (geoJsons == undefined || geoJsons.length === 0) {
        return
      }
      const sa1s = geoJsons[0]
      const propertyRequestUrl = axios.getUri({
        url: `${this.geoserverHost}/geoserver/sa1_emissions/ows`,
        params: {
          service: "WFS",
          version: "1.0.0",
          request: "GetFeature",
          outputFormat: "application/json",
          typeName: "sa1_emissions:sa1_emissions_all_cars",
          propertyname: `(SA12018_V1_00,VKT,AREA_SQ_KM,${this.co2PrefixedFuelTypes})`,
          cql_filter: `UR2023_V1_00_NAME ILIKE '${this.urbanAreaName}'`
        }
      });
      const propertyJson = await axios.get(propertyRequestUrl);
      const emissionsData = propertyJson.data.features as { properties: Sa1Emissions }[]
      const colorScale = chroma.scale(chroma.brewer.Reds);
      const sa1Entities = sa1s.entities.values;
      const sa1IdColumnName = "SA12018_V1_00";
      for (const entity of sa1Entities) {
        if (entity.polygon == undefined || entity.properties == undefined)
          continue;
        const entityData = emissionsData.find((emissionReading: { properties: Sa1Emissions }) => emissionReading.properties[sa1IdColumnName] == entity.properties?.[sa1IdColumnName]?.getValue())
        let polyGraphics: Cesium.PolygonGraphics
        if (entityData == undefined) {
          polyGraphics = new Cesium.PolygonGraphics({show: false})
        } else {
          const {vkt, co2} = this.getStyleInputVariables(entityData.properties)
          const color = colorScale(vkt / 50000)
          polyGraphics = new Cesium.PolygonGraphics({
            show: true,
            extrudedHeight: co2 / 5,
            material: new Cesium.Color(...color.gl()),
            outlineColor: new Cesium.Color(...color.darken().gl()),
          });
        }
        polyGraphics.merge(entity.polygon)
        entity.polygon = polyGraphics;

      }
      console.log("Loading ended")
    },

  },
  computed: {
    fuelTypes(): string[] {
      return this.vktUseRates.map(vktUseRate => vktUseRate.fuel_type)
    },

    co2PrefixedFuelTypes(): string {
      const fuelTypesPrefixed = this.fuelTypes.map(fuelType => {
        const fuelTypeNoSpaces = fuelType.replace(" ", "_");
        return `CO2_${fuelTypeNoSpaces}`;
      });
      return fuelTypesPrefixed.join(",")
    },

    totals(): { CO2: number, VKT: number } {
      let co2Sum = 0;
      for (const {fuel_type, weight, CO2} of this.vktUseRates) {
        const defaultWeight = this.sliderDefaultValues.find((defVal) => defVal.name === fuel_type)?.value;
        if (defaultWeight !== undefined) {
          co2Sum += (weight / defaultWeight) * CO2
        }
      }

      const VKT = this.vktUseRates.reduce((partialSum, entry) => partialSum + entry.VKT, 0)
      return {VKT, CO2: co2Sum}
    },

    formattedTotals(): { CO2: string, VKT: string } {
      const co2Rounded = parseInt(roundToFixed(this.totals.CO2));
      const vktRounded = parseInt(roundToFixed(this.totals.VKT * 1000));
      const CO2 = `${co2Rounded.toLocaleString()} Tonnes / Year`
      const VKT = `${vktRounded.toLocaleString()} km / Year`
      return {CO2, VKT}
    }
  }
});
</script>

<style>
#legend {
  position: absolute;
  bottom: 40px;
  right: 30px;
  height: 175px;
}

#control-card {
  position: absolute;
  top: 55px;
  min-width: 25em;
}

</style>
