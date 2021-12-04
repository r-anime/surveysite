<template>
  <template v-if="surveyResultsData">
    <h1 class="page-title">{{ pageTitle }}</h1>
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

    <h3 class="section-title">Popularity</h3>
    <h5 class="subsection-title">Most Popular Anime Series</h5>
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.popularity.value)" :resultName="resultsType.popularity.name"/>

    <button class="btn title-color w-100 collapsed mt-4" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-thing-rename-this" aria-expanded="false" aria-controls="collapse-thing-rename-this">
      <h4>
        <span class="show-if-collapsed">Show</span>
        <span class="show-if-not-collapsed">Hide</span>
        Popularity - By Gender
      </h4>
    </button>
    <div class="row collapse" id="collapse-thing-rename-this">
      <div class="col col-6">
        <SimpleResultsTable :ranking="getRanking(resultsType.popularityMale.value)" :resultName="resultsType.popularityMale.name" :top="5"/>
      </div>
      <div class="col col-6">
        <SimpleResultsTable :ranking="getRanking(resultsType.popularityFemale.value)" :resultName="resultsType.popularityFemale.name" :top="5"/>
      </div>
      <div class="col col-6">
        <SimpleResultsTable :ranking="getRanking(resultsType.popularityRatioMale.value)" :resultName="resultsType.popularityRatioMale.name" :top="5"/>
      </div>
      <div class="col col-6">
        <SimpleResultsTable :ranking="getRanking(resultsType.popularityRatioFemale.value)" :resultName="resultsType.popularityRatioFemale.name" :top="5"/>
      </div>
    </div>

    <h3 class="section-title">Impressions</h3>
    <h5 class="subsection-title">
      {{ surveyIsPreseason ? 'Most (and Least) Anticipated Anime of the Season' : 'Best (and Worst) Anime of the Season' }}
    </h5>
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.score.value)" :resultName="resultsType.score.name"/>

    <h3 class="section-title">Anime OVAs / ONAs / Movies / Specials</h3>
    <h5 class="subsection-title">Most Popular Anime OVAs / ONAs / Movies / Specials</h5>
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.popularity.value, false)" :resultName="resultsType.popularity.name"/>
    
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
import { getSurveyApiUrl, getSurveyName, isAnimeSeries } from '@/util/helpers';
import NotificationService from '@/util/notification-service';
import _ from 'lodash';
import { Vue, Options } from 'vue-class-component';
import AgeDistributionChart from './components/AgeDistributionChart.vue';
import GenderDistributionChart from './components/GenderDistributionChart.vue';
import SimpleResultsTable from './components/SimpleResultsTable.vue';
import TableWithTop3 from './components/TableWithTop3.vue';

interface SurveyResultsData {
  results: Record<number, Record<ResultsType, number>>;
  anime: Record<number, AnimeData>;
  survey: SurveyData;
  miscellaneous: {
    responseCount: number;
    ageDistribution: Record<number, number>;
    genderDistribution: Record<Gender, number>;
  };
}

@Options({
  components: {
    AgeDistributionChart,
    GenderDistributionChart,
    SimpleResultsTable,
    TableWithTop3,
    AnimeNames,
    AnimeImages,
  },
})
export default class SurveyResults extends Vue {
  /* eslint-disable @typescript-eslint/no-non-null-assertion */
  surveyResultsData: SurveyResultsData|null = null;
  surveyIsPreseason = true;
  pageTitle?: string;
  averageAge?: string;

  readonly resultsType: Record<string, { value: ResultsType, name: string }> = {
    // Someone please tell me why "hyphens: auto" doesn't work unless I add hyphens manually
    popularity: { value: ResultsType.POPULARITY, name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty' },
    popularityMale: { value: ResultsType.POPULARITY_MALE, name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Male)' },
    popularityFemale: { value: ResultsType.POPULARITY_FEMALE, name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Female)' },
    popularityRatioMale: { value: ResultsType.GENDER_POPULARITY_RATIO, name: 'Male:Female' },
    popularityRatioFemale: { value: ResultsType.GENDER_POPULARITY_RATIO_INV, name: 'Female:Male' },
    score: { value: ResultsType.SCORE, name: 'Sco\u00ADre' },
  };

  async mounted(): Promise<void> {
    const response = await Ajax.get<SurveyResultsData>(getSurveyApiUrl(this.$route) + 'results/');
    if (Response.isErrorData(response.data)) {
      NotificationService.pushMsgList(response.getGlobalErrors(), 'danger');

      this.$router.push({name: 'Index'});
      return;
    }

    this.surveyResultsData = response.data;
    this.surveyIsPreseason = this.surveyResultsData.survey.isPreseason;
    this.averageAge = _.sum(
      Object.entries(this.surveyResultsData.miscellaneous.ageDistribution).map(([ageStr, percentage]) => Number(ageStr) * percentage / 100)
    ).toFixed(2);
    this.pageTitle = getSurveyName(this.surveyResultsData.survey) + ' Results!';
  }

  getRanking(resultsType: ResultsType, forAnimeSeries = true, ascending = false): { anime: AnimeData, result: number }[] {
    let resultsTable: { anime: AnimeData, result: number }[] = [];

    const animeIds = Object.keys(this.surveyResultsData!.results);
    animeIds.forEach(animeIdStr => {
      const animeId = Number(animeIdStr);
      const animeData = this.surveyResultsData!.anime[animeId];
      if (isAnimeSeries(animeData) !== forAnimeSeries) return;

      resultsTable.push({
        anime: animeData,
        result: this.surveyResultsData!.results[animeId][resultsType],
      });
    });
    resultsTable = resultsTable.filter(item => item.result != null);
    resultsTable.sort((a, b) => a.result - b.result);

    if (!ascending) resultsTable.reverse();
    return resultsTable;
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/main'; // TODO: Include only what's necessary, this is inefficient

.section-title {
  @extend .title-color;
  @extend .rounded, .shadow, .mt-4, .p-3;
}

.subsection-title {
  @extend .text-center, .mt-4;
}
</style>