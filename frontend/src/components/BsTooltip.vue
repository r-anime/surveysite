<template>
  <i class="bi bi-info-circle-fill" ref="tooltipElement" data-bs-toggle="tooltip" :data-bs-title="text"></i>
</template>

<script setup lang="ts">
import { Tooltip } from 'bootstrap';
import { onBeforeUnmount, onMounted, ref } from 'vue';


defineProps<{
  text: string;
}>();

const tooltipElement = ref<Element | null>(null);
let bsTooltip: Tooltip | null = null;

onMounted(() => {
  if (tooltipElement.value) {
    bsTooltip = new Tooltip(tooltipElement.value, { trigger: 'hover focus' });
  }
});

onBeforeUnmount(() => {
  bsTooltip?.dispose();
});
</script>
