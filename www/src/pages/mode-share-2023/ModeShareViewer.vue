<template>
  <!-- The component that renders a CO2/VKT map for a given area of SA1s -->
  <div class="full-screen">
    <iframe
      :title="`Mode share flow map ${this.urbanAreaName}`"
      :src=flowMapSrcUrl
      width="100%"
      height="1080px"
      allowfullscreen
    />
  </div>
</template>

<script lang="ts">
import axios from "axios";
import {MapViewer} from 'geo-visualisation-components/src/components';
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
      geoserverHost: `${process.env.VUE_APP_GEOSERVER_HOST}:${process.env.VUE_APP_GEOSERVER_PORT}`,
      sheetId: undefined as string | undefined
    }
  },

  async created() {
    this.sheetId = await this.fetchSheetId()
  },

  methods: {
    async fetchSheetId(): Promise<string> {
      const propertyRequestUrl = axios.getUri({
        url: `${this.geoserverHost}/geoserver/sa2_mode_share/ows`,
        params: {
          service: "WFS",
          version: "1.0.0",
          request: "GetFeature",
          outputFormat: "application/json",
          typeName: "sa2_mode_share:flow_sheets",
          propertyname: "(sheet_url)",
          cql_filter: `urban_area ILIKE '${this.urbanAreaName}'`
        }
      })
      const propertyJson = await axios.get(propertyRequestUrl)
      const features = propertyJson.data.features as { properties: { urban_area: string, sheet_url: string } }[]
      const sheet_url = new URL(features[0].properties.sheet_url)
      return sheet_url.pathname.split("/").pop() as string
    }
  },

  computed: {
    flowMapSrcUrl(): string {
      return `https://www.flowmap.blue/${this.sheetId}`
    }
  }

});
</script>

<style>
.full-screen {
  overflow: hidden;
  height: 100%;
  width: 100%
}
</style>
