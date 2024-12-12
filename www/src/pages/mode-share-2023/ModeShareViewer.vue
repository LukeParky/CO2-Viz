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
    <ColorLegend
      id="legend"
      class="card"
      :legend-steps="legendSteps"
      axis-label="Total commuters"
    />
  </div>
</template>

<script lang="ts">
import * as Cesium from "cesium";
import chroma from "chroma-js";
import {MapViewer} from 'geo-visualisation-components/src/components';
import {MapViewerDataSourceOptions} from "geo-visualisation-components/src/types";
import Vue from "vue";

import ColorLegend, {HexColor, LegendStep} from "@/components/ColorLegend.vue";
import axios from "axios";
import {roundToFixed} from "@/utils";
import CesiumInfoBox from "@/pages/mode-share-2023/CesiumInfoBox.vue";

export default Vue.extend({
  name: "Co2Sa1Viewer",
  components: {
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
      colorScale: chroma.scale(chroma.brewer.Blues),
      modeShareColorScalingFactor: 2500,
    }
  },

  async mounted() {
    const geojson = await this.loadSa2s()
    this.dataSources.geoJsonDataSources = [geojson]
  },

  methods: {
    createDescriptionCallbackProp(entityProperties: Cesium.PropertyBag): Cesium.CallbackProperty {
      let descriptionBody: string | undefined;
      return new Cesium.CallbackProperty(() => {
        if (descriptionBody === undefined) {
          // Generate table rows dynamically
          const InfoBoxConstructor = Vue.extend(CesiumInfoBox)
          const instance = new InfoBoxConstructor({propsData: {entityProperties}})
          // Mount the component to a temporary div, then extract the HTML string
          instance.$mount();
          descriptionBody = instance.$el.outerHTML;
        }
        return descriptionBody;
      }, true);
    },

    async loadSa2s(): Promise<Cesium.GeoJsonDataSource> {
      console.log("Loading started")

      const geoserverUrl = axios.getUri({
        url: `${this.geoserverHost}/geoserver/sa2_mode_share/ows`,
        params: {
          service: "WFS",
          version: "1.0.0",
          request: "GetFeature",
          outputFormat: "application/json",
          typeName: "sa2_mode_share:mode_share_2023",
          cql_filter: `UR2023_V1_00_NAME ILIKE '${this.urbanAreaName}'`
        }
      })

      const sa2s = await Cesium.GeoJsonDataSource.load(geoserverUrl, {
        fill: Cesium.Color.fromAlpha(Cesium.Color.ROYALBLUE, 1),
        stroke: Cesium.Color.ROYALBLUE.darken(0.5, new Cesium.Color()),
        strokeWidth: 10
      });

      for (const entity of sa2s.entities.values) {
        if (entity.polygon == undefined || entity.properties == undefined)
          continue;
        const netOutflowScale = entity.properties["Total commuters"] / this.modeShareColorScalingFactor
        const color = this.colorScale(netOutflowScale)
        // console.log(entity.description)
        // if (entity.description) {
        //   console.log(entity.description.getValue(Cesium.JulianDate.now(), undefined))
        // }
        entity.description = this.createDescriptionCallbackProp(entity.properties)
        const polyGraphics = new Cesium.PolygonGraphics({
          show: true,
          material: new Cesium.Color(...color.gl()),
          outlineColor: new Cesium.Color(...color.darken().gl()),
        });

        polyGraphics.merge(entity.polygon)
        entity.polygon = polyGraphics;
      }
      console.log("Loading ended")
      return sa2s;
    },


  },
  computed: {
    legendSteps(): LegendStep[] {
      const numberOfSteps = 5;
      const steps = [] as LegendStep[]
      for (let i = 0; i <= numberOfSteps; i++) {
        const scaleProportion = (i / numberOfSteps)
        const outflowValue = scaleProportion * this.modeShareColorScalingFactor
        const outflowRounded = parseInt(roundToFixed(outflowValue)).toLocaleString()
        const outflowColor = this.colorScale(scaleProportion).hex() as HexColor
        steps.push({
          label: outflowRounded,
          color: outflowColor
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
  bottom: 0;
  right: 30px;
}
</style>
