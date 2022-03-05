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
              <div v-if="surveyIsUpcoming(surveysInSeason.preseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset clickable">
                <IndexSurvey :survey="surveysInSeason.preseasonSurvey"/>
              </div>
              <router-link v-else :to="getSurveyRoute(surveysInSeason.preseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset clickable">
                <IndexSurvey :survey="surveysInSeason.preseasonSurvey"/>
              </router-link>
            </template>
            <div v-else class="col col-lg-6 col-12 border p-3 d-lg-block bg-unavailable"></div>

            <template v-if="surveysInSeason.postseasonSurvey">
              <div v-if="surveyIsUpcoming(surveysInSeason.postseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset clickable">
                <IndexSurvey :survey="surveysInSeason.postseasonSurvey"/>
              </div>
              <router-link v-else :to="getSurveyRoute(surveysInSeason.postseasonSurvey)" class="col col-lg-6 col-12 border p-3 d-lg-block text-decoration-none text-reset clickable">
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
import { AnimeSeason, SurveyData } from '@/util/data';
import _ from 'lodash';
import NotificationService from '@/util/notification-service';
import { RouteLocationRaw } from 'vue-router';
import { getSeasonName } from '@/util/helpers';
import HttpService from '@/util/http-service';
import { IndexSurveyData } from './data/index-survey-data';
import dayjs from 'dayjs';


@Options({
  components: {
    IndexSurvey,
  },
})
export default class Index extends Vue {
  surveys: IndexSurveyData[] = [];
  surveyData: {
    year: number,
    surveys: {
      season: AnimeSeason,
      preseasonSurvey?: SurveyData,
      postseasonSurvey?: SurveyData,
    }[],
  }[] = [];

  async created(): Promise<void> {
    await HttpService.get<IndexSurveyData[]>('api/index/', this.getSeasonData, failureResponse => {
      NotificationService.pushMsgList(failureResponse.errors.global ?? ['An unknown error occurred'], 'danger');
    });
  }

  surveyIsUpcoming(survey: SurveyData): boolean {
    return dayjs() < dayjs(survey.openingEpochTime);
  }

  surveyIsFinished(survey: SurveyData): boolean {
    return dayjs(survey.closingEpochTime) < dayjs();
  }

  getSeasonName = getSeasonName;

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
  }

  getSurveyRoute(survey: IndexSurveyData): RouteLocationRaw {
    return {
      name: this.surveyIsFinished(survey) ? 'SurveyResultsSummary' : 'SurveyForm',
      params: {
        year: survey.year,
        season: survey.season,
        preOrPost: survey.isPreseason ? 'pre' : 'post',
      },
    };
  }

  // TODO: This should use pagination, the survey list obtained from the API should get appended to the already obtained survey list.
  async getSeasonData(newSurveys: IndexSurveyData[]): Promise<void> {
    // No need to get distinct surveys here as the _.find() takes care of that
    const surveys = newSurveys.concat(this.surveys);

    // [[2020 surveys], [2019 surveys], ...]
    const surveysOrderedGroupedByYear = _.orderBy(_.groupBy(surveys, 'year'), ['0.year'], ['desc']);

    const latestYear = (_.maxBy(surveys, 'year') ?? { year: 0 }).year;
    const earliestYear = (_.minBy(surveys, 'year') ?? { year: 0 }).year;

    // Group surveys by year, and then season (keeping gaps between year/seasons)
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
        });
      }

      return {
        year: surveyYearGroup[0].year,
        surveys: surveysOrderedGroupedBySeason,
      };
    });

    this.surveys = surveys;
    this.surveyData = surveyData;
  }
}
</script>


<style lang="scss" scoped>
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

.text-season {
  hyphens: auto;
  font-size: 90%;
}
</style>
