<template>
  <div id="balanced-slider">
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
      <label
        :for="`slider-${i}`"
        :disabled="disabled"
      >
        {{ initValue.name }}: {{ roundToFixed(reactiveValues[i], 2) }}%
      </label>
    </div>
    <b-button
      @click="$emit('submit', reactiveValues)"
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

<script>
export default {
  name: "BalancedSlider",

  props: {
    initValues: {
      type: Array,
      required: true,
      validator: function (arr) {
        if (arr.length === 0) {
          console.error("initValues must have values")
          return false; // Array must have values
        }
        if (!arr.every(elem => elem.value >= 0 && elem.value <= 100)){
          console.error("All initValues must be between 0 and 100")
          return false; // All element values must be between 0 and 100
        }
        const sum = arr.reduce((partialSum, elem) => partialSum + elem.value, 0)
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
      for (const [i, initValue] of this.initValues.entries()) {
        if (i === 0) {
          reactedValues.push(newValue)
        } else {
          const weight = initValue.value / (100 - this.initValues[0].value)
          const updatedSubValue = weight * (100 - newValue)
          reactedValues.push(updatedSubValue)
        }
      }
      this.$emit('input', newValue)
      this.$emit('change-sliders', reactedValues)
      this.reactiveValues = reactedValues
    }
  },

  methods: {
    onResetDefaultClicked() {
      this.value = this.initValues[0].value
      this.$emit('submit', this.reactiveValues)
    },
    roundToFixed(number, decimalPlaces = 0) {
      const factorForIntegerRounding = 10 ** decimalPlaces
      return (Math.round(number * factorForIntegerRounding) / factorForIntegerRounding).toFixed(decimalPlaces);
    },
  }
}
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
