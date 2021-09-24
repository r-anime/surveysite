<template>
  {{ $route.path }}
</template>

<script lang="ts">
import { Vue, Options } from "vue-class-component";

@Options({

})
export default class SurveyResults extends Vue {}
</script>