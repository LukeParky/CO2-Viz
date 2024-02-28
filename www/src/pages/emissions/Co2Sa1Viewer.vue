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
      <h2>Scenario Controller</h2>
      <p>
        Baseline CO2:
        <span class="value">{{ formattedTotals.baselineCo2 }}</span>
      </p>
      <p>
        Scenario CO2:
        <span class="value">{{ formattedTotals.CO2 }}</span>
        <span
          class="value"
          :class="percentageChangeClass.CO2"
        >
          ( {{ percentageChanges.CO2 }})&nbsp
        </span>
      </p>
      <BalancedSlider
        ref="balanced-slider"
        v-if="sliderDefaultValues.length > 0"
        :init-values="sliderDefaultValues"
        @submit="changeUseRates($event)"
      />
      <p>
        Baseline Vehicle Km Travelled:
        <span class="value">{{ formattedTotals.baselineVKT }}</span>
      </p>
      <p>
        Scenario Vehicle Km Travelled:
        <span class="value">{{ formattedTotals.VKT }}</span>
      </p>
      <div class="vkt-adjuster">
        <label for="vkt-slider">Adjust Scenario VKT</label>
        <input
          id="vkt-slider"
          type="range"
          min="0"
          max="100"
          step="1"
          v-model="VKTSlider"
        >
        <span class="value">
          <input
            id="vkt-spinner"
            type="number"
            v-model="VKTSlider"
            min="0"
            max="100"
          >
          <label for="vkt-spinner">%</label>
        </span>
      </div>
      <b-button
        @click="onUpdateClicked"
        size="sm"
      >
        Update
      </b-button>
      <b-button
        @click="onResetDefaultClicked"
        size="sm"
      >
        Reset to baseline
      </b-button>
    </div>
    <ColorLegend
      id="legend"
      class="card"
      :legend-steps="legendSteps"
      axis-label="'000 Vehicle km / year"
    />
  </div>
</template>

<script lang="ts">
import axios from "axios";
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components/src/components';
import {MapViewerDataSourceOptions} from "geo-visualisation-components/src/types";
import Vue from "vue";

import BalancedSlider from "@/components/BalancedSlider";
import ColorLegend, {HexColor, LegendStep} from "@/components/ColorLegend.vue";
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
    ColorLegend,
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
      baseLayer: new Cesium.ImageryLayer(new Cesium.OpenStreetMapImageryProvider({}), {saturation: 0}),
      geoserverHost: `${process.env.VUE_APP_GEOSERVER_HOST}:${process.env.VUE_APP_GEOSERVER_PORT}`,
      dataSources: {geoJsonDataSources: []} as MapViewerDataSourceOptions,
      cesiumApiToken: process.env.VUE_APP_CESIUM_ACCESS_TOKEN,
      vktUseRates: [] as { fuel_type: string, VKT: number, CO2: number, weight: number }[],
      baselineCo2: 0,
      baselineVKT: 0,
      VKT: 0,
      VKTSlider: 100 as string | number,
      sliderDefaultValues: [] as { name: string, value: number }[],
      colorScale: chroma.scale(chroma.brewer.Reds),
      vktColorScalingFactor: 50000,
      co2HeightScalingFactor: 5,
    }
  },

  async created() {
    this.vktUseRates = await this.fetchVktSums();
    this.sliderDefaultValues = this.vktUseRates.map(obj => ({name: obj.fuel_type, value: obj.weight}))
    this.baselineCo2 = this.vktUseRates.reduce((partialSum, entry) => partialSum + entry.CO2, 0);
    this.baselineVKT = this.vktUseRates.reduce((partialSum, entry) => partialSum + entry.VKT, 0);
    this.VKT = this.baselineVKT;
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

    onUpdateClicked() {
      const balancedSlider = this.$refs['balanced-slider'] as Vue & { onUpdateClicked: () => void }
      this.VKT = this.VKTSlider as number / 100 * this.baselineVKT;
      balancedSlider.onUpdateClicked();
    },

    onResetDefaultClicked() {
      const balancedSlider = this.$refs['balanced-slider'] as Vue & { onResetDefaultClicked: () => void }
      this.VKTSlider = 100;
      this.VKT = this.baselineVKT;
      balancedSlider.onResetDefaultClicked();
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
      co2 = co2 * this.VKT / this.baselineVKT;
      const vkt = sa1.VKT * this.VKT / this.baselineVKT;
      return {area_sq_km: sa1.AREA_SQ_KM, vkt, co2}
    },

    getColorFromVkt(vkt: number): chroma.Color {
      return this.colorScale(vkt / this.vktColorScalingFactor);
    },

    getExtrudedHeightFromCo2(co2: number): number {
      return co2 / this.co2HeightScalingFactor;
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
          const color = this.getColorFromVkt(vkt);
          const extrudedHeight = this.getExtrudedHeightFromCo2(co2);
          polyGraphics = new Cesium.PolygonGraphics({
            extrudedHeight,
            show: true,
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
      co2Sum = co2Sum * this.VKT / this.baselineVKT;
      return {VKT: this.VKT, CO2: co2Sum};
    },

    formattedTotals(): { CO2: string, VKT: string, baselineCo2: string, baselineVKT: string } {
      const co2Rounded = parseInt(roundToFixed(this.totals.CO2));
      const vktRounded = parseInt(roundToFixed(this.totals.VKT * 1000));
      const baselineCo2Rounded = parseInt(roundToFixed(this.baselineCo2))
      const baselineVKTRounded = parseInt(roundToFixed(this.baselineVKT * 1000));

      const CO2 = `${co2Rounded.toLocaleString()} Tonnes / Year`
      const VKT = `${vktRounded.toLocaleString()} km / Year`
      const baselineCo2 = `${baselineCo2Rounded.toLocaleString()} Tonnes / Year`
      const baselineVKT = `${baselineVKTRounded.toLocaleString()} km / Year`


      return {CO2, VKT, baselineCo2, baselineVKT}
    },

    percentageChanges(): { CO2: string, VKT: string } {
      let percentSignCO2 = ""
      if (this.totals.CO2 < this.baselineCo2)
        percentSignCO2 = "- "
      else if (this.totals.CO2 > this.baselineCo2)
        percentSignCO2 = "+ "
      const percentageChangeCO2 = roundToFixed(
        Math.abs(this.totals.CO2 - this.baselineCo2) / this.baselineCo2 * 100,
        2)
      const CO2 = `${percentSignCO2}${percentageChangeCO2} %`

      let percentSignVKT = ""
      if (this.totals.VKT < this.baselineVKT)
        percentSignVKT = "- "
      else if (this.totals.VKT > this.baselineVKT)
        percentSignVKT = "+ "
      const percentageChangeVKT = roundToFixed(
        Math.abs(this.totals.VKT - this.baselineVKT) / this.baselineVKT * 100,
        2)
      const VKT = `${percentSignVKT}${percentageChangeVKT} %`


      return {CO2, VKT}
    },

    percentageChangeClass(): { CO2: string, VKT: string } {
      let co2Class = "";
      if (this.totals.CO2 < this.baselineCo2)
        co2Class = "good-color"
      else if (this.totals.CO2 > this.baselineCo2)
        co2Class = "bad-color"

      let vktClass = "";
      if (this.totals.VKT < this.baselineVKT)
        vktClass = "good-color"
      else if (this.totals.VKT > this.baselineVKT)
        vktClass = "bad-color"
      return {CO2: co2Class, VKT: vktClass}
    },

    legendSteps(): LegendStep[] {
      const numberOfSteps = 5;
      const steps = [] as LegendStep[]
      for (let i = 0; i < numberOfSteps; i++) {
        const scaleProportion = (i / numberOfSteps)
        const vktValue = scaleProportion * this.vktColorScalingFactor
        const vktRounded = parseInt(roundToFixed(vktValue)).toLocaleString()
        const vktColor = this.colorScale(scaleProportion).hex() as HexColor
        steps.push({
          label: vktRounded,
          color: vktColor
        });
      }
      return steps;
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

.bad-color {
  color: #b51a28;
}

.good-color {
  color: #367f2e;
}

.vkt-adjuster {
  padding-right: 10px;
}

.vkt-adjuster input[type=range] {
  min-width: 10em;
  margin-left: 1em;
}

.btn {
  float: right;
  margin: 15px 5px 5px 5px
}

</style>
