<template>
  <!-- The component that renders a CO2/VKT map for a given area of SA1s -->
  <div class="full-height">
    <MapViewer
      :init-lat="initLat"
      :init-long="initLong"
      :init-height="initHeight"
      :init-base-layer="baseLayerProvider"
      :cesium-access-token="cesiumApiToken"
      :data-sources="dataSources"
    />
    <ColorLegend
      id="legend"
      class="card"
      :legend-steps="legendSteps"
      axis-label="Net Inflow/Outflow"
    />
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components';
import type {MapViewerDataSourceOptions} from "geo-visualisation-components";
import {computed, onMounted, ref} from "vue";

import ColorLegend from "@/components/ColorLegend.vue";
import type {HexColor, LegendStep} from "@/components/ColorLegend.vue";

import {roundToFixed} from "@/utils";


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


const baseLayerProvider = new Cesium.OpenStreetMapImageryProvider({});
const geoserverHost = `${import.meta.env.VITE_GEOSERVER_HOST}:${import.meta.env.VITE_GEOSERVER_PORT}`;
const cesiumApiToken = import.meta.env.VITE_CESIUM_ACCESS_TOKEN;
const colorScale = chroma.scale(chroma.brewer.RdYlBu);

const dataSources = ref<MapViewerDataSourceOptions>({});

onMounted(async () => {
  const geojson = await loadSa2s()
  dataSources.value = {geoJsonDataSources: [geojson]}
  await styleSa2s();
})

async function loadSa2s(): Promise<Cesium.GeoJsonDataSource> {
  const geoserverUrl = axios.getUri({
    url: `${geoserverHost}/geoserver/sa2_mode_share/ows`,
    params: {
      service: "WFS",
      version: "1.0.0",
      request: "GetFeature",
      outputFormat: "application/json",
      typeName: "sa2_mode_share:mode_share_2023",
      cql_filter: `UR2023_V1_00_NAME ILIKE '${props.urbanAreaName}'`
    }
  })

  const sa2s = await Cesium.GeoJsonDataSource.load(geoserverUrl, {
    fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 1),
    stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
    strokeWidth: 10
  });
  return sa2s;
}

async function styleSa2s(): Promise<void> {
  console.log("Loading started")
  const geoJsons = dataSources.value.geoJsonDataSources;
  if (geoJsons == undefined || geoJsons.length === 0) {
    return
  }
  const sa2s = geoJsons[0]
  for (const entity of sa2s.entities.values) {
    if (entity.polygon == undefined || entity.properties == undefined)
      continue;
    let polyGraphics: Cesium.PolygonGraphics
    console.log(entity.properties)
    const color = colorScale(entity.properties.Net_outflow / 2000)
    const extrudedHeight = 4
    polyGraphics = new Cesium.PolygonGraphics({
      extrudedHeight,
      show: true,
      material: new Cesium.Color(...color.gl()),
      outlineColor: new Cesium.Color(...color.darken().gl()),
    });

    polyGraphics.merge(entity.polygon)
    entity.polygon = polyGraphics;

  }
  console.log("Loading ended")
}

const legendSteps = computed<LegendStep[]>(() => {
  const numberOfSteps = 5;
  const steps = [] as LegendStep[]
  for (let i = 0; i < numberOfSteps; i++) {
    const scaleProportion = (i / numberOfSteps)
    const netFlowValue = scaleProportion * 100
    const netFlowRounded = parseInt(roundToFixed(netFlowValue)).toLocaleString()
    const netFlowColour = colorScale(scaleProportion).hex() as HexColor
    steps.push({
      label: netFlowRounded,
      color: netFlowColour
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

#control-card button {
  float: right;
  margin: 15px 5px 5px 5px
}

.vkt-adjuster input[type=range] {
  min-width: 10em;
  margin-left: 1em;
}

</style>
