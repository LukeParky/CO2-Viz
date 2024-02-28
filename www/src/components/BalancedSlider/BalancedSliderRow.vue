<template>
  <div class="slider-row">
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
        :value="spinnerValueDisplay"
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
import {roundToFixed} from "@/utils";

let componentUuid = 0;

export default Vue.extend({
  name: "BalancedSliderRow",
  components: {LockCheckbox},

  props: {
    name: String,
    value: [Number, String],
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
    spinnerValueDisplay(): string {
      return roundToFixed(this.value as number, 2)
    },
  }
});
</script>

<style scoped>
.slider-row {
  padding: 5px;
}
</style>
