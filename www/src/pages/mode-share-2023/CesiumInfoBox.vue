<template>
  <div>
    <div class="plot-container" style="height: 500px;">
      <Plotly
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
import {Plotly} from "vue-plotly";

export default Vue.extend({
  components: {Plotly},
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
          text: "Mode shares of commuters",
          yref: 0,
          font: {
            color: '#ffffff'
          }
        }
      }
    }
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
.plot-container {
  height: 700px;
}
.cesium-infoBox-defaultTable {
  margin-top: 20px;
}
</style>

