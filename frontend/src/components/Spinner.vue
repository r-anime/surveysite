<template>
  <div :class="['d-flex', { 'justify-content-center': center }]">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";

@Options({
  props: {
    center: Boolean,
  },
})
export default class Spinner extends Vue {}
</script>
