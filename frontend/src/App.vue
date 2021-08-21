<template>
  <div class="mb-5">
    <TheNavbar/>
  </div>
  <router-view/>
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
