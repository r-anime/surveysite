<template>
  {{ survey }}
</template>

<script lang="ts">
import { SurveyData } from '@/util/data';
import { Options, Vue } from 'vue-class-component';

@Options({
  props: {
    survey: {} as SurveyData
  }
})
export default class Survey extends Vue {
  survey!: SurveyData;
}
</script>

<style scoped lang="scss">
</style>
