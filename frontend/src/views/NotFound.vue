<template>
  Could not find "{{ $route.path }}"
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
  components: {
  },
})
export default class NotFound extends Vue {}
</script>
