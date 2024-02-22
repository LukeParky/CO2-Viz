<template>
  <div id="balanced-slider">
    <div v-for="(initValue, i) in initValues" :key="i">
      <input
        :id="`slider-${i}`"
        class="slider"
        type="range"
        min="0"
        max="100"
        v-model.number="sliderValues[i]"
        @input="onChange(i)"
        :disabled="disabled"
      >
      <label
        :for="`slider-${i}`"
        :disabled="disabled"
      >
        {{ initValue.name }}: {{ formattedSliderValue(i) }}
      </label>
    </div>
    <b-button
      @click="$emit('submit', sliderValues)"
      size="sm"
      :disabled="disabled"
    >
      Update
    </b-button>
    <b-button
      @click="onResetDefaultClicked"
      size="sm"
      :disabled="disabled"
    >
      Reset to default
    </b-button>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

import {roundToFixed} from "@/utils";

interface SliderItem {
  name: string,
  value: number
}

export default Vue.extend({
  name: "BalancedSlider",

  props: {
    initValues: {
      type: Array as () => Array<SliderItem>,
      required: true,
      validator: function (initValues: Array<SliderItem>) {
        if (initValues.length === 0) {
          console.error("initValues must have values")
          return false; // Array must have values
        }
        if (!initValues.every(elem => elem.value >= 0 && elem.value <= 100)) {
          console.error("All initValues must be between 0 and 100")
          return false; // All element values must be between 0 and 100
        }
        const sum = initValues.reduce((partialSum, elem) => partialSum + elem.value, 0)
        const sum2dp = Math.round(sum * 100) / 100
        if (sum2dp !== 100) {
          console.error(`initValues must sum to 100, instead got ${sum}`)
          return false; // The element values must sum to 100
        }
        return true;
      },
      default() {
        return []
      }
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      sliderValues: this.initValues.map(initValue => initValue.value)
    }
  },

  methods: {
    onResetDefaultClicked() {
      this.sliderValues = this.initValues.map(initValue => initValue.value)
      this.$emit('submit', this.sliderValues)
    },

    formattedSliderValue(i: number): string {
      return `${roundToFixed(this.sliderValues[i], 2)}%`
    },

    onChange(sliderIndex: number) {
      const changedSliderValue = this.sliderValues[sliderIndex]
      const reactedValues = [];
      for (const [i, initValue] of this.initValues.entries()) {
        if (i === sliderIndex) {
          reactedValues.push(changedSliderValue)
        } else {
          const weight = initValue.value / (100 - this.initValues[sliderIndex].value)
          const updatedSubValue = weight * (100 - changedSliderValue)
          reactedValues.push(updatedSubValue)
        }
      }
      this.$emit('input', reactedValues)
      this.$emit('change-sliders', reactedValues)
      this.sliderValues = reactedValues

    },
  }
});
</script>

<style scoped>
#balanced-slider {
  padding: 5px;
}

.btn {
  margin: 2px
}

label {
  padding-left: 10px;
}
</style>
