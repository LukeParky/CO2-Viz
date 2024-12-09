<template>
  <input
    ref="spinner"
    type="number"
    :value="spinnerDisplayValue"
    :min="min"
    :max="max"
    @input.stop.prevent="handleInputs($event)"
    @focusout="handleInputs($event)"
    @keyup.enter="handleInputs($event)"
  >
</template>

<script lang="ts">
import {defineComponent} from "vue";
import {roundToFixed} from "@/utils";

export default defineComponent({
  name: "RoundedSpinner",

  props: {
    value: {
      type: Number,
      default: 0,
    },
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
  },

  methods: {
    handleInputs(event: Event & InputEvent): void {
      if (event?.inputType === "insertText") {
        event.stopImmediatePropagation();
      } else {
        console.log(event)
        this.$emit("submit", event);
      }
    }
  }
});
</script>

<style scoped>
</style>
