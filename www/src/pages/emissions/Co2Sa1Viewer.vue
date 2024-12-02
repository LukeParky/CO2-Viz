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
          ( {{ percentageChanges.CO2 }})&nbsp;
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
      <div>
        <button
          @click="onUpdateClicked"
          class="btn btn-secondary btn-sm"
        >
          Update
        </button>
        <button
          @click="onResetDefaultClicked"
          class="btn btn-secondary btn-sm"
        >
          Reset to baseline
        </button>
      </div>
    </div>
    <ColorLegend
      id="legend"
      class="card"
      :legend-steps="legendSteps"
      axis-label="'000 Vehicle km / year"
    />
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components';
import type {MapViewerDataSourceOptions} from "geo-visualisation-components";
import {computed, defineProps, onMounted, ref, useTemplateRef} from "vue";

import BalancedSlider from "@/components/BalancedSlider";
import type {ClickToUpdateComponent} from "@/components/BalancedSlider";
import ColorLegend from "@/components/ColorLegend.vue";
import type {HexColor, LegendStep} from "@/components/ColorLegend.vue";

import {roundToFixed} from "@/utils";

interface Sa1Emissions {
  SA12018_V1_00: number,
  AREA_SQ_KM: number,
  CO2?: number,
  VKT: number,

  [k: `CO2_${string}`]: number | undefined,
}

const props = defineProps({
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
)


const baseLayer = undefined;
const geoserverHost = `${import.meta.env.VITE_GEOSERVER_HOST}:${import.meta.env.VITE_GEOSERVER_PORT}`;
const cesiumApiToken = import.meta.env.VITE_CESIUM_ACCESS_TOKEN;
const colorScale = chroma.scale(chroma.brewer.Reds);
const vktColorScalingFactor = 50000;
const co2HeightScalingFactor = 5;

const VKTSlider = ref<string | number>(100);
const dataSources = ref<MapViewerDataSourceOptions>({});
const vktUseRates = ref<{ fuel_type: string, VKT: number, CO2: number, weight: number }[]>([]);
const baselineCo2 = ref<number>(0);
const baselineVKT = ref<number>(0);
const VKT = ref<number>(0);
const sliderDefaultValues = ref<{ name: string, value: number }[]>([]);
const balancedSlider = useTemplateRef<ClickToUpdateComponent>('balanced-slider')

vktUseRates.value = await fetchVktSums();
baselineCo2.value = vktUseRates.value.reduce((partialSum, entry) => partialSum + entry.CO2, 0);
baselineVKT.value = vktUseRates.value.reduce((partialSum, entry) => partialSum + entry.VKT, 0);
VKT.value = baselineVKT.value
sliderDefaultValues.value = vktUseRates.value.map(obj => ({name: obj.fuel_type, value: obj.weight}))

onMounted(async () => {
  const geojson = await loadSa1s()
  dataSources.value = {geoJsonDataSources: [geojson]}
  await styleSa1s();
})

async function loadSa1s(): Promise<Cesium.GeoJsonDataSource> {
  const geoserverUrl = axios.getUri({
    url: `${geoserverHost}/geoserver/sa1_emissions/ows`,
    params: {
      service: "WFS",
      version: "1.0.0",
      request: "GetFeature",
      outputFormat: "application/json",
      typeName: "sa1_emissions:sa1s",
      cql_filter: `UR2023_V1_00_NAME ILIKE '${props.urbanAreaName}'`
    }
  })

  const sa1s = await Cesium.GeoJsonDataSource.load(geoserverUrl, {
    fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 1),
    stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
    strokeWidth: 10
  });
  return sa1s;
}

async function fetchVktSums(): Promise<{ fuel_type: string, VKT: number, CO2: number, weight: number }[]> {
  const propertyRequestUrl = axios.getUri({
    url: `${geoserverHost}/geoserver/sa1_emissions/ows`,
    params: {
      service: "WFS",
      version: "1.0.0",
      request: "GetFeature",
      outputFormat: "application/json",
      typeName: "sa1_emissions:vkt_sum",
      propertyname: "(fuel_type,VKT,CO2)",
      cql_filter: `UR2023_V1_00_NAME ILIKE '${props.urbanAreaName}'`
    }
  })
  const propertyJson = await axios.get(propertyRequestUrl)
  const features = propertyJson.data.features as { properties: { fuel_type: string, VKT: number, CO2: number } }[]

  const fuel_to_vkts = features.map(feature => feature.properties)
  const total_vkt = fuel_to_vkts.reduce((partialSum, entry) => partialSum + entry.VKT, 0)
  return fuel_to_vkts.map(entry => ({...entry, weight: entry.VKT / total_vkt * 100}))
}

function onUpdateClicked() {
  VKT.value = VKTSlider.value as number / 100 * baselineVKT.value;
  balancedSlider.value?.onUpdateClicked();
}

function onResetDefaultClicked() {
  VKTSlider.value = 100;
  VKT.value = baselineVKT.value;
  balancedSlider.value?.onResetDefaultClicked();
}

function changeUseRates(changeEvent: number[]) {
  for (const i in changeEvent) {
    vktUseRates.value[i].weight = changeEvent[i]
  }
  styleSa1s()
}

function getInfoBoxTable(sa1Emissions: Sa1Emissions, co2: number, vkt: number): Cesium.Property | undefined {
  const infoBox = `
    <div class="cesium-infoBox-description">
      <table class="cesium-infoBox-defaultTable">
        <tbody>
          <tr><th>SA12018_V1_00</th><td>${sa1Emissions.SA12018_V1_00}</td></tr>
          <tr><th>Area (km&sup2)</th><td>${roundToFixed(sa1Emissions.AREA_SQ_KM, 4)}</td></tr>
          <tr><th>CO2 (T/Y)</th><td>${roundToFixed(co2)}</td></tr>
          <tr><th>VKT (km/Y)</th><td>${roundToFixed(vkt * 1000)}</td></tr>
        </tbody>
      </table>
    </div>
  `
  return infoBox as unknown as Cesium.Property
}

function getStyleInputVariables(sa1: Sa1Emissions): { area_sq_km: number, vkt: number, co2: number } {
  let co2 = sa1.CO2;
  if (co2 === undefined) {
    co2 = 0;
    for (const {fuel_type, weight} of vktUseRates.value) {
      const defaultWeight = sliderDefaultValues.value.find((defVal) => defVal.name === fuel_type)?.value;
      const sa1FuelCo2Contribution = sa1[`CO2_${fuel_type}`]
      if (defaultWeight !== undefined && sa1FuelCo2Contribution !== undefined) {
        co2 += (weight / defaultWeight) * sa1FuelCo2Contribution
      }
    }
  }
  co2 = co2 * VKT.value / baselineVKT.value;
  const vkt = sa1.VKT * VKT.value / baselineVKT.value;
  return {area_sq_km: sa1.AREA_SQ_KM, vkt, co2}
}

function getColorFromVkt(vkt: number): chroma.Color {
  return colorScale(vkt / vktColorScalingFactor);
}

function getExtrudedHeightFromCo2(co2: number): number {
  return co2 / co2HeightScalingFactor;
}

async function styleSa1s(): Promise<void> {
  console.log("Loading started")
  const geoJsons = dataSources.value.geoJsonDataSources;
  if (geoJsons == undefined || geoJsons.length === 0) {
    return
  }
  const sa1s = geoJsons[0]
  const propertyRequestUrl = axios.getUri({
    url: `${geoserverHost}/geoserver/sa1_emissions/ows`,
    params: {
      service: "WFS",
      version: "1.0.0",
      request: "GetFeature",
      outputFormat: "application/json",
      typeName: "sa1_emissions:sa1_emissions_all_cars",
      propertyname: `(SA12018_V1_00,VKT,AREA_SQ_KM,${co2PrefixedFuelTypes.value})`,
      cql_filter: `UR2023_V1_00_NAME ILIKE '${props.urbanAreaName}'`
    }
  });
  const propertyJson = await axios.get(propertyRequestUrl);
  const emissionsData = propertyJson.data.features as { properties: Sa1Emissions }[]
  const sa1Entities = sa1s.entities.values;
  const sa1IdColumnName = "SA12018_V1_00";
  for (const entity of sa1Entities) {
    if (entity.polygon == undefined || entity.properties == undefined)
      continue;
    const entityData = emissionsData.find((emissionReading: {
      properties: Sa1Emissions
    }) => emissionReading.properties[sa1IdColumnName] == entity.properties?.[sa1IdColumnName]?.getValue())
    let polyGraphics: Cesium.PolygonGraphics
    if (entityData == undefined) {
      polyGraphics = new Cesium.PolygonGraphics({show: false})
    } else {
      const {vkt, co2} = getStyleInputVariables(entityData.properties)
      entity.description = getInfoBoxTable(entityData.properties, co2, vkt)

      const color = getColorFromVkt(vkt);
      const extrudedHeight = getExtrudedHeightFromCo2(co2);
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
}

const fuelTypes = computed<string[]>(() => {
  return vktUseRates.value.map(vktUseRate => vktUseRate.fuel_type)
});

const co2PrefixedFuelTypes = computed<string>(() => {
  const fuelTypesPrefixed = fuelTypes.value.map(fuelType => {
    const fuelTypeNoSpaces = fuelType.replace(" ", "_");
    return `CO2_${fuelTypeNoSpaces}`;
  });
  return fuelTypesPrefixed.join(",")
});

const totals = computed<{ CO2: number, VKT: number }>(() => {
  let co2Sum = 0;
  for (const {fuel_type, weight, CO2} of vktUseRates.value) {
    const defaultWeight = sliderDefaultValues.value.find((defVal) => defVal.name === fuel_type)?.value;
    if (defaultWeight !== undefined) {
      co2Sum += (weight / defaultWeight) * CO2
    }
  }
  co2Sum = co2Sum * VKT.value / baselineVKT.value;
  return {VKT: VKT.value, CO2: co2Sum};
});

const formattedTotals = computed<{CO2: string, VKT: string, baselineCo2: string, baselineVKT: string}>(() => {
  const co2Rounded = parseInt(roundToFixed(totals.value.CO2));
  const vktRounded = parseInt(roundToFixed(totals.value.VKT * 1000));
  const baselineCo2Rounded = parseInt(roundToFixed(baselineCo2.value))
  const baselineVKTRounded = parseInt(roundToFixed(baselineVKT.value * 1000));

  const CO2 = `${co2Rounded.toLocaleString()} Tonnes / Year`
  const VKT = `${vktRounded.toLocaleString()} km / Year`
  const baseCo2Formatted = `${baselineCo2Rounded.toLocaleString()} Tonnes / Year`
  const baseVKTFormatted = `${baselineVKTRounded.toLocaleString()} km / Year`


  return {CO2, VKT, baselineCo2: baseCo2Formatted, baselineVKT: baseVKTFormatted}
});

const percentageChanges = computed<{ CO2: string, VKT: string }>(() => {
  let percentSignCO2 = ""
  if (totals.value.CO2 < baselineCo2.value)
    percentSignCO2 = "- "
  else if (totals.value.CO2 > baselineCo2.value)
    percentSignCO2 = "+ "
  const percentageChangeCO2 = roundToFixed(
    Math.abs(totals.value.CO2 - baselineCo2.value) / baselineCo2.value * 100,
    2)
  const CO2 = `${percentSignCO2}${percentageChangeCO2} %`

  let percentSignVKT = ""
  if (totals.value.VKT < baselineVKT.value)
    percentSignVKT = "- "
  else if (totals.value.VKT > baselineVKT.value)
    percentSignVKT = "+ "
  const percentageChangeVKT = roundToFixed(
    Math.abs(totals.value.VKT - baselineVKT.value) / baselineVKT.value * 100,
    2)
  const VKT = `${percentSignVKT}${percentageChangeVKT} %`


  return {CO2, VKT}
});

const percentageChangeClass = computed<{ CO2: string, VKT: string }>(() => {
  let co2Class = "";
  if (totals.value.CO2 < baselineCo2.value)
    co2Class = "good-color"
  else if (totals.value.CO2 > baselineCo2.value)
    co2Class = "bad-color"

  let vktClass = "";
  if (totals.value.VKT < baselineVKT.value)
    vktClass = "good-color"
  else if (totals.value.VKT > baselineVKT.value)
    vktClass = "bad-color"
  return {CO2: co2Class, VKT: vktClass}
});

const legendSteps = computed<LegendStep[]>(() => {
  const numberOfSteps = 5;
  const steps = [] as LegendStep[]
  for (let i = 0; i < numberOfSteps; i++) {
    const scaleProportion = (i / numberOfSteps)
    const vktValue = scaleProportion * vktColorScalingFactor
    const vktRounded = parseInt(roundToFixed(vktValue)).toLocaleString()
    const vktColor = colorScale(scaleProportion).hex() as HexColor
    steps.push({
      label: vktRounded,
      color: vktColor
    });
  }
  return steps;
});

</script>

<style>
#legend {
  position: absolute;
  bottom: 0;
  right: 30px;
}

#control-card {
  position: absolute;
  top: 55px;
  min-width: 25em;
}

#control-card button {
  float: right;
  margin: 15px 5px 5px 5px
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

</style>
