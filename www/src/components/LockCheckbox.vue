<template>
  <span>
    <input
      :id="id"
      type="checkbox"
      :checked="checked"
      @change.stop="$emit('change', ($event.target as HTMLInputElement).checked)"
    >
    <label :for="id">
      <img
        :src="`${checked ? '/font-awesome/solid-lock.svg' : '/font-awesome/solid-lock-open.svg'}`"
        :alt="`${checked ? 'Locked padlock' : 'Unlocked padlock'}`"
      />
    </label>
  </span>
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "LockCheckbox",

  model : {
    prop: 'checked',
    event: 'change'
  },

  props: {
    id: {
      type: String,
      required: true
    },
    checked: {
      type: Boolean,
      default: false
    }
  },

});
</script>

<style scoped>
input[type=checkbox] {
  display: none;
}

label img {
  cursor: pointer;
  height: 1em;
  width: 1em;
  vertical-align: baseline;
}
</style>
