<template>
  <template v-if="surveyResultsData">
    <h1 class="mb-4 mx-n2 p-3 shadow bg-primary bg-opacity-75 text-light">{{ pageTitle }}</h1>
    <div class="row">
      <div class="col-md-8">
        <div class="row"><div class="col">
          <p>
            Thanks everyone for filling in this survey! There were {{ surveyResultsData.miscellaneous.responseCount }} responses,
            and the average age of everyone who answered was {{ averageAge }}.
          </p>
          <p>
            Anime with a popularity of less than 2% will not be displayed here, as their data may be inaccurate.
          </p>
        </div></div>
        <div class="row mt-2"><div class="col">
          <AgeDistributionChart :ageDistribution="surveyResultsData.miscellaneous.ageDistribution"/>
        </div></div>
      </div>
      <div class="col-md-4">
        <GenderDistributionChart :genderDistribution="surveyResultsData.miscellaneous.genderDistribution"/>
      </div>
    </div>

    <div class="row">
      <div class="col col-4">
        Popularity test
      </div>
      <div class="col">
        <SimpleResultsTable :ranking="getRanking(1)" :top="3"/>
      </div>
    </div>

    <div class="row">
      <div class="col col-4">
        Score test
      </div>
      <div class="col">
        <SimpleResultsTable :ranking="getRanking(11)" :top="3"/>
      </div>
    </div>
    
    {{ $route.path }}
    <br/>
    {{ surveyResultsData }}
  </template>
</template>

<script lang="ts">
import Ajax, { Response } from '@/util/ajax';
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { AnimeData, Gender, ResultsType, SurveyData } from '@/util/data';
import { getSurveyApiUrl, getSurveyName } from '@/util/helpers';
import NotificationService from '@/util/notification-service';
import _ from 'lodash';
import { Vue, Options } from 'vue-class-component';
import AgeDistributionChart from './components/AgeDistributionChart.vue';
import GenderDistributionChart from './components/GenderDistributionChart.vue';
import SimpleResultsTable from './components/SimpleResultsTable.vue';

interface SurveyResultsData {
  results: Record<number, Record<ResultsType, number>>;
  anime: Record<number, AnimeData>;
  survey: SurveyData;
  miscellaneous: {
    responseCount: number;
    ageDistribution: Record<number, number>;
    genderDistribution: Record<Gender, number>;
  }
}

@Options({
  components: {
    AgeDistributionChart,
    GenderDistributionChart,
    SimpleResultsTable,
    AnimeNames,
    AnimeImages,
  },
})
export default class SurveyResults extends Vue {
  /* eslint-disable @typescript-eslint/no-non-null-assertion */
  surveyResultsData: SurveyResultsData|null = null;
  pageTitle?: string;
  averageAge?: string;

  async mounted(): Promise<void> {
    const response = await Ajax.get<SurveyResultsData>(getSurveyApiUrl(this.$route) + 'results/');
    if (Response.isErrorData(response.data)) {
      NotificationService.pushMsgList(response.getGlobalErrors(), 'danger');

      this.$router.push({name: 'Index'});
      return;
    }

    this.surveyResultsData = response.data;
    this.averageAge = _.sum(
      Object.entries(this.surveyResultsData.miscellaneous.ageDistribution).map(([ageStr, percentage]) => Number(ageStr) * percentage / 100)
    ).toFixed(2);
    this.pageTitle = getSurveyName(this.surveyResultsData.survey) + ' Results!';
  }

  getRanking(resultsType: ResultsType, ascending = false): { anime: AnimeData, result: number }[] {
    let resultsTable: { anime: AnimeData, result: number }[] = [];

    const animeIds = Object.keys(this.surveyResultsData!.results);
    animeIds.forEach(animeId => resultsTable.push({
      anime: this.surveyResultsData!.anime[Number(animeId)],
      result: this.surveyResultsData!.results[Number(animeId)][resultsType],
    }));
    resultsTable = resultsTable.filter(item => item.result != null);
    resultsTable.sort((a, b) => a.result - b.result);

    if (!ascending) resultsTable.reverse();
    return resultsTable;
  }
}
</script>