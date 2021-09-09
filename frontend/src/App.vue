<template>
  <div class="mb-5">
    <TheNavbar/>
  </div>
  <div class="container-md">
    <router-view/>
  </div>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import TheNavbar from '@/components/TheNavbar.vue';

@Options({
  components: {
    TheNavbar,
  },
})
export default class App extends Vue {}
</script>
