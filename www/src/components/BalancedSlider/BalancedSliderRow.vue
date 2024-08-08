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
      @input="onInput(parseFloat(($event.target as HTMLInputElement).value))"
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
      <RoundedSpinner
        :id="`spinner-${uuid}`"
        ref="spinner"
        type="number"
        :value="value"
        @input="onInput($event.target.value)"
      />
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
import {defineComponent} from "vue";
import LockCheckbox from "@/components/LockCheckbox.vue";
import RoundedSpinner from "@/components/RoundedSpinner.vue";

let componentUuid = 0;

export default defineComponent({
  name: "BalancedSliderRow",
  components: {RoundedSpinner, LockCheckbox},

  props: {
    name: String,
    value: Number,
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
      internalLocked: this.locked,
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

});
</script>

<style scoped>
.slider-row {
  padding: 5px;
}
</style>
