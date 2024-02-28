<template>
  <div>
    <input
      :id="`slider-${uuid}`"
      ref="slider"
      type="range"
      min="0"
      max="100"
      :value="value"
      :disabled="locked || disabled"
      @input="onInput($event.target.value)"
    >
    <LockCheckbox
      :id="`slider-lock-${uuid}`"
      :checked="locked"
      @change="$emit('lock-change', $event)"
    />
    <label
      :for="`slider-${uuid}`"
      :disabled="disabled"
    >
      {{ name }}:
    </label>
    <span class="value">
      <input
        :id="`spinner-${uuid}`"
        ref="spinner"
        type="number"
        :value="value"
        min="0"
        max="100"
        :disabled="locked || disabled"
        @input="onInput($event.target.value)"
      >
      <label
        :for="`spinner-${uuid}`"
        :disabled="disabled"
      >
        %
      </label>
    </span>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import LockCheckbox from "@/components/LockCheckbox.vue";

let componentUuid = 0;

export default Vue.extend({
  name: "BalancedSliderRow",
  components: {LockCheckbox},

  props: {
    name: {
      type: String
    },
    value: {
      type: Number
    },
    locked: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    }
  },

  data() {
    return {
      uuid: componentUuid,
      internalLocked: this.locked
    }
  },

  created() {
    componentUuid++;
  },

  methods: {
    onInput(newValue: number) {
      this.$emit('input', newValue)
    }
  },

  computed: {
    // sliderValueDisplay: {
    //   get(): number {
    //     return parseFloat(roundToFixed(this.value, 2))
    //   },
    //   set(newValues: number[]) {
    //     console.log('set')
    //     console.log(newValues)
    //     this.value = newValue;
    //   }
    // },
  }
});
</script>

<style scoped>
input[type=range] {
  min-width: 12em;
  vertical-align: middle;
}

input[type=number] {
  max-width: 4em;
}

label {
  display: inline;
  min-width: 10em;
}
</style>
