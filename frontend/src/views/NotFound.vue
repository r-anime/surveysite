<template>
  Could not find {{ $route.path ? `"${$route.path}"` : 'that page' }}.
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
})
export default class NotFound extends Vue {}
</script>
