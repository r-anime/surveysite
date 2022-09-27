<template>
  <div class="mb-5">
    <TheNavbar />
  </div>
  <div class="container-md mb-5">
    <RouterView />
  </div>
  <div>
    <TheModals />
  </div>
  <div>
    <TheNotifications />
  </div>
</template>

<script setup lang="ts">
import TheNavbar from '@/components/TheNavbar.vue';
import TheNotifications from '@/components/TheNotifications.vue';
import TheModals from './components/TheModals.vue';
</script>
