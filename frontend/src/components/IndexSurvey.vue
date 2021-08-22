<template>
  <div class="row row-cols-1 h-100">
    <div class="col mb-1">
      <h5>
        {{ getSurveyName() }}
        <small class="text-muted" style="font-size: 80%;">Finished</small>
      </h5>
    </div>
    
    <div v-for="(surveyAnimeList, resultstype) in survey.animeResults" :key="resultstype" class="col mb-3">
      <div class="row mb-2">
        <div class="col bg-primary bg-opacity-75 text-light rounded py-1 px-2 w-100">
          {{ getResultstypeName(resultstype) }}
        </div>
      </div>
      <IndexSurveyAnime v-for="(surveyAnime, idx) in surveyAnimeList" :key="idx" :surveyAnime="surveyAnime" class="mb-1" :class="idx==0 ? '' : 'd-lg-flex d-none'"/>
    </div>
  </div>
</template>

<script lang="ts">
import { ResultsType, SurveyData } from '@/util/data';
import { getSeasonName } from '@/util/helpers';
import IndexSurveyAnime from '@/components/IndexSurveyAnime.vue';
import { Options, Vue } from 'vue-class-component';

@Options({
  components: {
    IndexSurveyAnime
  },
  props: {
    survey: {
      type: Object,
    }
  },
  data() {
    return {

    }
  },
  methods: {
    getSurveyName() {
      const survey = this.survey as SurveyData;
      return `The ${survey.isPreseason ? 'Start' : 'End'} of ${getSeasonName(survey.season)} ${survey.year} Survey`;
    },
    getResultstypeName(resultstype: string): string {
      const resultstypeNumber = Number(resultstype);
      switch (resultstypeNumber) {
        case ResultsType.POPULARITY:
          return 'Most popular anime';
        case ResultsType.SCORE:
          return this.survey.isPreseason ? 'Most anticipated series' : 'Most highly regarded series';
        default:
          return ResultsType[resultstypeNumber];
      }
    }
  }
})
export default class IndexSurvey extends Vue {
  survey!: SurveyData;
}
</script>
