<template>
  <div class="row row-cols-1">
    
    <div class="col" v-for="(surveysInYear, idx0) in surveyData" :key="idx0">

      <div class="row justify-content-center">
        <div class="col col-11 d-flex align-items-center">
          <h3 :class="idx0>0 ? 'mt-5' : ''">{{ surveysInYear.year }}</h3>
        </div>
      </div>
      
      <div class="row justify-content-center" v-for="(surveysInSeason, idx1) in surveysInYear.surveys" :key="idx1">
        <div class="col col-2 col-sm-1 border rounded-start d-flex justify-content-center align-items-center text-center" :class="'bg-'+getSeasonName(surveysInSeason.season).toLowerCase()">
          <div class="row row-cols-1">
            <div class="col">
              <i class="bi" :class="getSeasonIconClass(surveysInSeason.season)"></i>
            </div>
            <div class="col text-season fw-bold">
              <span>{{ getSeasonName(surveysInSeason.season) }}</span>
            </div>
          </div>
        </div>
        <div class="col col-9 col-sm-10">
          <div class="row h-100">

            <template v-if="surveysInSeason.preseasonSurvey">
              <div v-if="surveyIsUpcoming(surveysInSeason.preseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset bg-survey">
                <IndexSurvey :survey="surveysInSeason.preseasonSurvey"/>
              </div>
              <router-link v-else :to="getSurveyUrl(surveysInSeason.preseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset bg-survey">
                <IndexSurvey :survey="surveysInSeason.preseasonSurvey"/>
              </router-link>
            </template>
            <div v-else class="col col-lg-6 col-12 border p-3 d-lg-block bg-unavailable"></div>

            <template v-if="surveysInSeason.postseasonSurvey">
              <div v-if="surveyIsUpcoming(surveysInSeason.postseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset bg-survey">
                <IndexSurvey :survey="surveysInSeason.postseasonSurvey"/>
              </div>
              <router-link v-else :to="getSurveyUrl(surveysInSeason.postseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset bg-survey">
                <IndexSurvey :survey="surveysInSeason.postseasonSurvey"/>
              </router-link>
            </template>
            <div v-else class="col col-lg-6 col-12 border p-3 d-lg-block bg-unavailable"></div>

          </div>
        </div>
        
      </div>

    </div>
  </div>
</template>


<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import IndexSurvey from './components/IndexSurvey.vue';
import Ajax, { Response } from '@/util/ajax';
import { AnimeResultsData, AnimeSeason, ImageData, ResultsType, SurveyData } from '@/util/data';
import _ from 'lodash';
import NotificationService from '@/util/notification-service';


export interface IndexSurveyData extends SurveyData {
  animeResults?: Record<ResultsType, AnimeResultsData[]>; // For finished surveys
  animeImages?: ImageData[];                              // For upcoming/ongoing suveys
}


@Options({
  components: {
    IndexSurvey,
  },
  data() {
    return {
      surveys: [],
      surveyData: [],
      _: _,
      console: console,
    }
  },
  methods: {
    surveyIsUpcoming(survey: SurveyData): boolean {
      return new Date() < new Date(survey.openingEpochTime);
    },
    surveyIsFinished(survey: SurveyData): boolean {
      return new Date(survey.closingEpochTime) < new Date();
    },

    getSeasonName(season: string): string {
      const seasonNumber = Number(season);
      const seasonNameUpper = AnimeSeason[seasonNumber];
      return seasonNameUpper.charAt(0) + seasonNameUpper.slice(1).toLowerCase()
    },

    getSeasonIconClass(season: string): string {
      const seasonNumber = Number(season);
      switch (seasonNumber) {
        case AnimeSeason.WINTER:
          return 'bi-snow';
        case AnimeSeason.SPRING:
          return 'bi-flower2';
        case AnimeSeason.SUMMER:
          return 'bi-sun';
        case AnimeSeason.FALL:
          return 'bi-tree';
        default:
          return '';
      }
    },

    getSurveyUrl(survey: IndexSurveyData): string {
      const preOrPost = survey.isPreseason ? 'pre' : 'post';
      const resultsOrEmpty = this.surveyIsFinished(survey) ? 'results/' : '';
      return `/survey/${survey.year}/${survey.season}/${preOrPost}/${resultsOrEmpty}`;
    },

    // In the future this should use pagination,
    // the survey list obtained from the API gets appended to the already obtained survey list.
    async getSeasonData() {
      const response = await Ajax.get<IndexSurveyData[]>('api/index/') ?? [];
      if (Response.isErrorData(response.data)) {
        NotificationService.pushMsgList(response.getGlobalErrors(), 'danger');
        return;
      }

      let surveys = response.data.concat(this.surveys);

      // [[2020 surveys], [2019 surveys], ...]
      const surveysOrderedGroupedByYear = _.orderBy(_.groupBy(surveys, 'year'), ['0.year'], ['desc']);

      const latestYear = (_.maxBy(surveys, 'year') ?? { year: 0 }).year;
      const earliestYear = (_.minBy(surveys, 'year') ?? { year: 0 }).year;

      // Just hover over surveyData to see what the end goal is here
      const surveyData = surveysOrderedGroupedByYear.map(surveyYearGroup => {
        // { 1: spring surveys, 3: fall surveys }
        const surveysGroupedBySeason = _.groupBy(surveyYearGroup, 'season');

        const latestSeason = latestYear === surveyYearGroup[0].year ?
          (_.maxBy(surveyYearGroup, 'season') ?? { season: AnimeSeason.FALL }).season :
          AnimeSeason.FALL;
        const earliestSeason = earliestYear === surveyYearGroup[0].year ?
          (_.minBy(surveyYearGroup, 'season') ?? { season: AnimeSeason.WINTER }).season :
          AnimeSeason.WINTER;

        const surveysOrderedGroupedBySeason: { season: AnimeSeason, preseasonSurvey?: SurveyData, postseasonSurvey?: SurveyData }[] = [];
        for (let season = latestSeason; season >= earliestSeason; season--) {
          const preseasonSurvey = _.find(surveysGroupedBySeason[season] ?? [], [ 'isPreseason', true ]);
          const postseasonSurvey = _.find(surveysGroupedBySeason[season] ?? [], [ 'isPreseason', false ]);
          surveysOrderedGroupedBySeason.push({
            season: season,
            preseasonSurvey: preseasonSurvey,
            postseasonSurvey: postseasonSurvey,
          })
        }

        return {
          year: surveyYearGroup[0].year,
          surveys: surveysOrderedGroupedBySeason,
        };
      });

      this.surveys = surveys;
      this.surveyData = surveyData;
    }
  },
  async created() {
    await this.getSeasonData();
  }
})
export default class Index extends Vue {}
</script>


<style lang="scss" scoped>
@import "@/../node_modules/bootstrap/scss/functions";
@import "@/../node_modules/bootstrap/scss/variables";
@import "@/../node_modules/bootstrap/scss/utilities";

.bi {
  font-size: 2rem;
}

.bg-winter {
  background-color: rgb(123, 171, 193);
}
.bg-spring {
  background-color: rgb(168, 215, 44);
}
.bg-summer {
  background-color: rgb(223, 129, 60);
}
.bg-fall {
  background-color: rgb(253, 215, 10);
}
.bg-unavailable {
  background-color: rgb(227, 227, 227)!important;
}
.bg-survey:hover {
  background-color: $gray-100;
}

.text-season {
  hyphens: auto;
  font-size: 90%;
}
</style>
