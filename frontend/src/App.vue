<template>
  <TheNavbar/>
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
export default class App extends Vue {};
</script>
