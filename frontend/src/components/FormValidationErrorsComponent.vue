<template>
  <div class="invalid-feedback" :id="id">
    <span v-for="(error, errorIdx) in (validationErrors ?? [])" :key="errorIdx">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  validationErrors?: string[];
  id: string;
}>();
</script>
