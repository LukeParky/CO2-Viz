<template>
  <div
    id="balanced-slider"
    :key="componentKey"
  >
    <BalancedSliderRow
      v-for="(initValue, i) in initValues"
      :ref="`slider-row-${i}`"
      :key="i"
      :name="initValue.name"
      v-model.number="sliderValues[i]"
      :locked="sliderLocks[i]"
      @input="onChange(i, $event)"
      @lock-change="onLockChange(i, $event)"
    />
  </div>
</template>

<script lang="ts">
import {type Component, defineComponent} from "vue";

import {roundToFixed} from "@/utils";
import BalancedSliderRow from "@/components/BalancedSlider/BalancedSliderRow.vue";

interface SliderItem {
  name: string,
  value: number
}

type VModel = Component & { value: number, $refs: Component[] }


export default defineComponent({
  name: "BalancedSlider",
  components: {
    BalancedSliderRow,
  },
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
      sliderLocks: new Array(this.initValues.length).fill(false) as boolean[],
      componentKey: 0,
    }
  },


  methods: {
    onUpdateClicked() {
      this.$emit('submit', this.sliderValues);
    },

    onResetDefaultClicked() {
      this.sliderLocks = this.sliderLocks.fill(false)
      this.sliderValues = this.initValues.map(initValue => initValue.value)
      this.$emit('submit', this.sliderValues)
    },

    formattedSliderValue(i: number): string {
      return `${roundToFixed(this.sliderValues[i], 2)}%`
    },

    async onChange(sliderIndex: number, sliderValue: number) {
      const lockedSum = this.getLockedSum();
      const maxChangedSliderValue = 100 - lockedSum
      const changedSliderValue = Math.min(sliderValue, maxChangedSliderValue)
      const reactedValues = [];
      for (const [i, initValue] of this.initValues.entries()) {
        if (i === sliderIndex) {
          reactedValues.push(changedSliderValue)
        } else if (this.sliderLocks[i]) {
          reactedValues.push(this.sliderValues[i])
        } else {
          let weight = initValue.value / (100 - this.initValues[sliderIndex].value - this.getLockedInitSum())
          const updatedSubValue = weight * (100 - changedSliderValue - lockedSum)
          reactedValues.push(updatedSubValue)
        }
      }
      this.$emit('input', reactedValues)
      this.$emit('change-sliders', reactedValues)
      this.sliderValues = reactedValues
      const rowComponent = this.$refs[`slider-row-${sliderIndex}`] as InstanceType<typeof BalancedSliderRow>[];
      const sliderComponent = rowComponent[0].$refs.slider as VModel;
      const spinnerComponent = rowComponent[0].$refs.spinner as VModel;
      await this.$nextTick()
      if (rowComponent[0].value != sliderComponent.value || rowComponent[0].value != spinnerComponent.value) {
        this.forceRerender()
      }
    },

    onLockChange(lockRowIndex: number, newIsLocked: boolean) {
      const numberLocked = this.sliderLocks
        .map(isLocked => +isLocked)
        .reduce((partialSum, current) => partialSum + current, 0)
      if (!newIsLocked || numberLocked < this.sliderLocks.length - 2) {
        this.sliderLocks[lockRowIndex] = newIsLocked;
      }
    },

    getLockedSum(): number {
      let lockedSum = 0;
      for (const [i, isLocked] of this.sliderLocks.entries()) {
        if (isLocked) {
          lockedSum += this.sliderValues[i];
        }
      }
      return lockedSum;
    },

    getLockedInitSum(): number {
      let lockedInitSum = 0;
      for (const [i, isLocked] of this.sliderLocks.entries()) {
        if (isLocked) {
          lockedInitSum += this.initValues[i].value;
        }
      }
      return lockedInitSum;
    },

    forceRerender() {
      this.componentKey++;
    }
  },

  computed: {
    sliderValuesDisplay: {
      get(): number[] {
        return this.sliderValues.map(sliderValue => parseFloat(roundToFixed(sliderValue, 2)))
      },
      set(newValues: number[]) {
        this.sliderValues = newValues;
      }
    },
  },
});
</script>

<style scoped>
#balanced-slider {
  min-width: inherit;
  padding: 5px;
}
</style>
