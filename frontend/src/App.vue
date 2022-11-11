<template>
  <div class="mb-5">
    <TheNavbarComponent />
  </div>
  <div class="container-md mb-5">
    <RouterView />
  </div>
  <div>
    <TheModalsComponent />
  </div>
  <div>
    <TheNotificationsComponent />
  </div>
</template>

<script setup lang="ts">
import TheNavbarComponent from '@/components/TheNavbarComponent.vue';
import TheNotificationsComponent from '@/components/TheNotificationsComponent.vue';
import TheModalsComponent from './components/TheModalsComponent.vue';
</script>
