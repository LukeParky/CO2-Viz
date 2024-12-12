<template>
  <div>
    <table class="cesium-infoBox-defaultTable">
      <tbody>
      <tr v-for="prop of entityProperties.propertyNames" :key="prop">
        <th>{{ prop }}</th>
        <td>{{ entityProperties[prop] }}</td>
      </tr>
      </tbody>
    </table>
  </div>
</template>
<script lang="ts">

import Vue, {PropType} from "vue";
import * as Cesium from "cesium";

export default Vue.extend({
  props: {
    entityProperties: {
      type: Object as PropType<Cesium.PropertyBag>,
      required: true
    }
  },
})
</script>
