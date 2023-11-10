<template>
  <div>
    <div v-for="(initValue, i) in initValues" :key="i">
      <input
        v-if="i === 0"
        :id="`slider-${i}`"
        class="slider"
        type="range"
        min="0"
        max="100"
        v-model.number="value"
        :disabled="disabled"
      >
      <input
        v-else
        :id="`slider-${i}`"
        class="slider"
        type="range"
        min="0"
        max="100"
        v-model="reactiveValues[i]"
        disabled
      >
      <label :for="`slider-${i}`">{{ initValue.name }} {{ roundToFixed(reactiveValues[i]) }}%</label>
    </div>
    <button @click="$emit('submit', reactiveValues)">Select percentages shares</button>
    <button @click="value = initValues[0].value">Reset to default</button>
  </div>
</template>

<script>
export default {
  name: "BalancedSlider",

  props: {
    initValues: {
      type: Array,
      required: true,
      validator: function (arr) {
        if (arr.length == 0) return false; // Array must have values
        if (!arr.every(elem => elem.value >= 0 && elem.value <= 100)) return false; // All element values must be between 0 and 100
        return (arr.reduce((partialSum, elem) => partialSum + elem.value, 0) === 100) // The element values must sum to 100
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
      value: null,
      reactiveValues: []
    }
  },

  created() {
    this.value = this.initValues[0].value;
  },

  watch: {
    value(newValue) {
      const reactedValues = [];
      console.log(this.initValues)
      for (const [i, initValue] of this.initValues.entries()) {
        if (i === 0) {
          reactedValues.push(newValue)
        } else {
          const weight = initValue.value / (100 - this.initValues[0].value)
          const updatedSubValue = weight * (100 - newValue)
          reactedValues.push(updatedSubValue)
        }
      }
      // console.log(reactedValues)
      this.$emit('input', newValue)
      this.$emit('change-sliders', reactedValues)
      this.reactiveValues = reactedValues
    }
  },

  methods: {
    roundToFixed(number, decimalPlaces = 0) {
      const factorForIntegerRounding = 10 ** decimalPlaces
      return (Math.round(number * factorForIntegerRounding) / factorForIntegerRounding).toFixed(decimalPlaces);
    },
  }
}
</script>

<style scoped>

</style>
