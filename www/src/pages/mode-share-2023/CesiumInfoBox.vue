<template>
  <div>
    <div style="height: 610px;">
      <PlotlyPlot
        ref="plot"
        :data="plotData"
        :layout="plotLayout"
        :display-mode-bar="false"
      />
    </div>
    <table class="cesium-infoBox-defaultTable">
      <tbody>
      <tr v-for="prop of propNames" :key="prop">
        <th>{{ prop }}</th>
        <td>{{ entityProperties[prop] }}</td>
      </tr>
      </tbody>
    </table>
  </div>
</template>
<script>

import Vue from "vue";
import {Plotly as PlotlyPlot} from "vue-plotly";

export default Vue.extend({
  components: {PlotlyPlot},
  props: {
    entityProperties: {
      required: true
    }
  },
  data() {
    return {
      plotLayout: {
        width: 450,
        title: {
          text: "Number of commuters by mode share",
          yref: 0,
          font: {
            color: '#ffffff'
          }
        }
      }
    }
  },
  mounted() {
    const plot = this.$refs.plot;
    const svgContainer = plot.$el.firstChild.firstChild
    const svgMain = svgContainer.firstChild
    svgMain.style.height = "550px";
    svgMain.style.width = "510px";
    const svgLast = svgContainer.lastChild
    svgLast.style.height = 0;
  },
  computed: {
    propNames() {
      console.log(this.entityProperties.propertyNames)
      return this.entityProperties.propertyNames
    },
    dataPropNames() {
      return this.propNames.filter(name => !(name.startsWith("SA2") || name.startsWith("UR2023")))
    },
    propValues() {
      return this.dataPropNames.map(name => this.entityProperties[name]._value)
    },
    plotData() {
      return [{
        x: this.dataPropNames,
        y: this.propValues,
        type: "bar",
      }]
    },
  }
})
</script>
<style>
.cesium-infoBox-defaultTable {
  margin-top: 20px;
}
.cesium-infoBox {
  max-width: 510px;
}
</style>

