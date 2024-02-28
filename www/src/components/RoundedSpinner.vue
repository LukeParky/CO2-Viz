<template>
  <input
    ref="spinner"
    type="number"
    :value="spinnerDisplayValue"
    :min="min"
    :max="max"
    @focusout="$emit('input', $event)"
    @keyup.enter="$emit('input', $event)"
  >
</template>

<script lang="ts">
import Vue from "vue";
import {roundToFixed} from "@/utils";

export default Vue.extend({
  name: "RoundedSpinner",

  props: {
    value: Number,
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
    },
    decimalPlaces: {
      type: Number,
      default: 2,
    },
  },

  computed: {
    spinnerDisplayValue(): string {
      return roundToFixed(this.value, this.decimalPlaces)
    }
  }
});
</script>

<style scoped>
</style>
