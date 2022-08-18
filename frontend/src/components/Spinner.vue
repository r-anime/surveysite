<template>
  <div :class="['d-flex', { 'justify-content-center': center }]">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  center?: boolean;
}>();
</script>
