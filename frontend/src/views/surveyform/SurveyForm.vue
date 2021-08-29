<template>
  <h1 class="mb-4 mx-n2 shadow">{{ surveyName }}</h1>
</template>

<script lang="ts">
import { SurveyData } from '@/util/data';
import { getSurveyName } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';

@Options({
  components: {
  },
  data() {
    return {
      survey: {
        year: Number(this.$route.params.year),
        season: Number(this.$route.params.season),
        isPreseason: (this.$route.params.preOrPost as string).toLowerCase() === 'pre',
      } as SurveyData,
      surveyName: '',
    }
  },
  mounted() {
    this.surveyName = this.survey ? getSurveyName(this.survey as SurveyData) : '';
  }
})
export default class Survey extends Vue {}
</script>
