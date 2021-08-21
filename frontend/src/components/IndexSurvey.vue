<template>
  <div class="row h-100">
    <div class="col col-12 mb-1">
      <h5>
        {{ getSurveyName() }}
        <small class="text-muted" style="font-size: 80%;">Finished</small>
      </h5>
    </div>
    
    <div class="col col-6 col-lg-12 mb-lg-3">
      <div class="row mb-1">
        <div class="col">
          <span>
            Most popular series
          </span>
        </div>
      </div>
      <div class="row align-items-center" style="font-size:70%;">
        <template v-for="(surveyAnime, idx1) in survey.mostPopularAnime" :key="idx1">
          <div class="col" :class="idx1==0 ? '' : 'd-lg-flex d-none'">
            <IndexSurveyAnime :surveyAnime="surveyAnime"/>
          </div>
        </template>
      </div>
    </div>
    
    <div class="col col-6 col-lg-12 mb-lg-3 mt-auto">
      <div class="row mb-1">
        <div class="col">
          <span>
            {{ survey.isPreseason ? 'Most anticipated series' : 'Most highly regarded series' }}
          </span>
        </div>
      </div>
      <div class="row align-items-center" style="font-size:70%;">
        <template v-for="(surveyAnime, idx1) in survey.bestAnime" :key="idx1">
          <div class="col" :class="idx1==0 ? '' : 'd-lg-flex d-none'">
            <IndexSurveyAnime :surveyAnime="surveyAnime"/>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { SurveyData } from '@/util/data';
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
    }
  }
})
export default class IndexSurvey extends Vue {
  survey!: SurveyData;
}
</script>
