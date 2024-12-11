<template>
  <div>
    <h2>Legend</h2>
    <p>{{ axisLabel }}</p>
    <div class="legend-container">
      <div class="legend-labels">
        <div
          v-for="step in legendSteps"
          class="legend-label"
        >
          {{ step.label }}
        </div>
      </div>
      <div class="legend-colors">
        <div
          class="color-box"
          :style="`height: ${legendSteps.length * 1.5}em; background-image: linear-gradient(${firstColour}, ${lastColour}`" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export type HexColor = `#${string}`

export interface LegendStep {
  color: HexColor,
  label: string,
}

export default Vue.extend({
  name: "ColorLegend",

  props: {
    disabled: {
      type: Boolean,
      default: false
    },
    legendSteps: {
      type: Array as () => Array<LegendStep>,
      required: true,
      validator: function (legendSteps: Array<LegendStep>): boolean {
        if (legendSteps.length < 2) {
          console.error("ColorLegend prop legendSteps must have length >= 2");
          return false;
        }
        return true;
      },
      default() {
        return [
          {value: 0, color: '#000000'},
          {value: 10, color: '#FFFFFF'}
        ]
      }
    },
    axisLabel: {
      type: String,
      required: true
    }
  },

  computed: {
    firstColour(): string {
      return this.legendSteps[0].color
    },

    lastColour(): string {
      return this.legendSteps[this.legendSteps.length - 1].color
    },
  }
});
</script>

<style scoped>
/* Styles for legend container */
.legend-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-family: Arial, sans-serif;
}

/* Styles for labels */
.legend-labels {
  display: flex;
  flex-direction: column;
  margin-right: 20px; /* Adjust as needed */
}

/* Styles for individual label */
.legend-label {
  margin-bottom: 5px; /* Adjust as needed */
}

/* Styles for color boxes */
.color-box {
  width: 20px;
  height: 20px;
  margin-left: 10px; /* Adjust as needed */
  border: 1px solid #ccc; /* Add border for better visibility */
}
</style>
