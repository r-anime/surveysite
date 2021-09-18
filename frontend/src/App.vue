<template>
  <div class="mb-5">
    <TheNavbar/>
  </div>
  <div class="container-md mb-5">
    <router-view/>
  </div>
  <div class="position-fixed bottom-0 start-50 translate-middle-x">
    <TheNotifications/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import TheNavbar from '@/components/TheNavbar.vue';
import TheNotifications from '@/components/TheNotifications.vue';

@Options({
  components: {
    TheNavbar,
    TheNotifications,
  },
})
export default class App extends Vue {}
</script>
