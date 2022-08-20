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
  <div class="position-fixed bottom-0 start-50 translate-middle-x" style="z-index:100000;"> <!-- Notifications ALWAYS have to be on top -->
    <TheNotifications />
  </div>
</template>

<script setup lang="ts">
import TheNavbar from '@/components/TheNavbar.vue';
import TheNotifications from '@/components/TheNotifications.vue';
import TheModals from './components/TheModals.vue';
</script>
