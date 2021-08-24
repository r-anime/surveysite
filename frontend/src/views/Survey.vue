<template>
  Survey {{ $route.params.year }} {{ $route.params.season }} {{ $route.params.preOrPost }}
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
  components: {
  },
})
export default class Survey extends Vue {}
</script>
