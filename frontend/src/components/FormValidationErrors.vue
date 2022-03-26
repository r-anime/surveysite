<template>
  <div class="invalid-feedback" :id="id">
    <span v-for="(error, errorIdx) in (validationErrors ?? [])" :key="errorIdx">{{ error }}</span>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from "vue-class-component";

@Options({
  props: {
    validationErrors: Array,
    id: String,
  }
})
export default class FormValidationErrors extends Vue {}
</script>
