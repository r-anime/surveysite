<template>
  <div class="row row-cols-1 h-100">
    <div class="col mb-1">
      <h5>
        {{ getSurveyName() }}
        <small v-if="new Date() > closingTime" class="text-muted" style="font-size:80%;">Finished</small>
        <span v-else-if="new Date() > openingTime" class="badge bg-primary rounded-pill" style="font-size:80%">Ongoing</span>
        <span v-else class="badge bg-secondary rounded-pill" style="font-size:80%">Upcoming</span>
      </h5>
    </div>
    
    <template v-if="new Date() > closingTime">
      <div v-for="(surveyAnimeList, resultstype) in survey.animeResults" :key="resultstype" class="col mb-3">
        <div class="row mb-2">
          <div class="col bg-primary bg-opacity-75 text-light rounded py-1 px-2 w-100">
            {{ getResultstypeName(resultstype) }}
          </div>
        </div>
        <IndexSurveyAnime v-for="(surveyAnime, idx) in surveyAnimeList" :key="idx" :surveyAnime="surveyAnime" class="mb-1" :class="idx==0 ? '' : 'd-lg-flex d-none'"/>
      </div>
    </template>

    <template v-else>
      <div class="col position-relative">
        <div class="row row-cols-lg-6 p-3 align-items-center opacity-25">
          <div v-for="(image, imageIdx) in survey.animeImages"
               :key="imageIdx"
               class="col p-1"
               :class="imageIdx>=8 ? 'd-lg-block d-none' : imageIdx>=6 ? 'd-md-block d-none' : ''">
            <img :src="image.urlSmall" :alt="image.name" class="img-fluid">
          </div>
        </div>

        <div class="row align-items-center justify-content-center h-100 w-100 position-absolute top-0 start-0">
          <div class="col text-center fs-1" style="text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);">
            {{ new Date() > openingTime ? 'Survey open!' : `Open ${openingTime.toLocaleString()}`}}
          </div>
        </div>
      </div>
    </template>

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
      openingTime: new Date((this.survey as SurveyData).openingEpochTime),
      closingTime: new Date((this.survey as SurveyData).closingEpochTime),
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
