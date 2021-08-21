<template>
  {{ survey }}
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    survey: {}
  }
})
export default class Survey extends Vue {
  survey!: any;
}
</script>

<style scoped lang="scss">
</style>
