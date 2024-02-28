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
        :disabled="sliderLocks[i] || disabled"
      >
      <LockCheckbox
        :id="`slider-lock-${i}`"
        v-model="sliderLocks[i]"
      />
      <label
        :for="`slider-${i}`"
        :disabled="disabled"
      >
        {{ initValue.name }}:
        <span class="value">{{ formattedSliderValue(i) }}</span>
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
      Reset to baseline
    </b-button>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

import {roundToFixed} from "@/utils";
import LockCheckbox from "@/components/LockCheckbox.vue";

interface SliderItem {
  name: string,
  value: number
}

export default Vue.extend({
  name: "BalancedSlider",
  components: {LockCheckbox},
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
      sliderValues: this.initValues.map(initValue => initValue.value),
      sliderLocks: new Array(this.initValues.length).fill(false) as boolean[]
    }
  },


  methods: {
    onResetDefaultClicked() {
      this.sliderLocks = this.sliderLocks.fill(false)
      this.sliderValues = this.initValues.map(initValue => initValue.value)
      this.$emit('submit', this.sliderValues)
    },

    formattedSliderValue(i: number): string {
      return `${roundToFixed(this.sliderValues[i], 2)}%`
    },

    onChange(sliderIndex: number) {
      const maxChangedSliderValue = 100 - this.lockedSum
      const changedSliderValue = Math.min(this.sliderValues[sliderIndex], maxChangedSliderValue)
      const reactedValues = [];
      for (const [i, initValue] of this.initValues.entries()) {
        if (i === sliderIndex) {
          reactedValues.push(changedSliderValue)
        } else if (this.sliderLocks[i]) {
          reactedValues.push(this.sliderValues[i])
        } else {
          let weight = initValue.value / (100 - this.initValues[sliderIndex].value - this.lockedInitSum)
          const updatedSubValue = weight * (100 - changedSliderValue - this.lockedSum)
          reactedValues.push(updatedSubValue)
        }
      }
      this.$emit('input', reactedValues)
      this.$emit('change-sliders', reactedValues)
      this.sliderValues = reactedValues

    },
  },

  computed: {
    lockedSum(): number {
      let lockedSum = 0;
      for (const [i, isLocked] of this.sliderLocks.entries()) {
        if (isLocked) {
          lockedSum += this.sliderValues[i];
        }
      }
      return lockedSum;
    },

    lockedInitSum(): number {
      let lockedInitSum = 0;
      for (const [i, isLocked] of this.sliderLocks.entries()) {
        if (isLocked) {
          lockedInitSum += this.initValues[i].value;
        }
      }
      return lockedInitSum;
    },
  }
});
</script>

<style scoped>
#balanced-slider {
  min-width: inherit;
  padding: 5px;
}

.btn {
  float: right;
  margin: 15px 5px 5px 5px
}

.slider {
  min-width: 12em;
  vertical-align: middle;
}

label {
  display: inline;
  min-width: 10em;
}
</style>
