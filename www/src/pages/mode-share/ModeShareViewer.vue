<template>
  <!-- The component that renders a CO2/VKT map for a given area of SA1s -->
  <div class="full-screen">
    <iframe
      src="https://www.flowmap.blue/1oZqsz8f0VlcmeLv35_OOe9TBDrTBWx4IhGIl9lodb2Q/c2bb2e1/embed"
      width="100%"
      height="1080px"
      frameborder="0"
      allowfullscreen
    />
  </div>
</template>

<script lang="ts">
import axios from "axios";
import * as Cesium from "cesium";
import {MapViewer} from 'geo-visualisation-components/src/components';
import {MapViewerDataSourceOptions} from "geo-visualisation-components/src/types";
import Vue from "vue";

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
    /** Initial height of the camera in metres. Default is 2000m */
    initHeight: {
      type: Number,
      default: 2000,
    },
    /** Urban area name for filtering areas, given from the StatsNZ Urban Rural dataset, UR2023_V1_00_NAME */
    urbanAreaName: {
      type: String,
      required: true
    }
  },

  data() {
    return {
      baseLayer: new Cesium.ImageryLayer(new Cesium.OpenStreetMapImageryProvider({}), {}),
      geoserverHost: `${process.env.VUE_APP_GEOSERVER_HOST}:${process.env.VUE_APP_GEOSERVER_PORT}`,
      dataSources: {geoJsonDataSources: []} as MapViewerDataSourceOptions,
      cesiumApiToken: process.env.VUE_APP_CESIUM_ACCESS_TOKEN,
    }
  },

  async mounted() {
    const geojson = await this.loadSa2s()
    this.dataSources.geoJsonDataSources = [geojson]
  },

  methods: {
    async loadSa2s(): Promise<Cesium.GeoJsonDataSource> {
      const geoserverUrl = axios.getUri({
        url: `${this.geoserverHost}/geoserver/sa2_mode_share/ows`,
        params: {
          service: "WFS",
          version: "1.0.0",
          request: "GetFeature",
          outputFormat: "application/json",
          typeName: "sa2_mode_share:sa2s",
          cql_filter: `UR2023_V1_00_NAME ILIKE '${this.urbanAreaName}'`
        }
      })

      return Cesium.GeoJsonDataSource.load(geoserverUrl, {
        fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 1),
        stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
        strokeWidth: 10
      });
    },
  },

});
</script>

<style>
.full-screen {
  overflow: hidden;
  height: 100%;
  width: 100%
}
</style>
