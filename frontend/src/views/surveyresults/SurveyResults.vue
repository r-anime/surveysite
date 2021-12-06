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
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.popularity)" :resultTypes="resultsType.popularity.resultTypes" :top="10"/>

    <div class="row justify-content-center mt-4">
      <div class="col col-11">
        <div class="row">
          <button class="btn title-color w-100 collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapsable-popularity-gender" aria-expanded="false" aria-controls="collapsable-popularity-gender">
            <h4>
              <span class="show-if-collapsed">Show</span>
              <span class="show-if-not-collapsed">Hide</span>
              Popularity - By Gender
            </h4>
          </button>
        </div>
        <div class="row collapse text-smaller border rounded" id="collapsable-popularity-gender">
          <h5 class="col col-12 subsection-title mb-1">Most Popular Anime Series by Gender</h5>
          <div class="col col-6 mt-3 pe-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.popularityMale)" :resultTypes="resultsType.popularityMale.resultTypes" :top="3"/>
          </div>
          <div class="col col-6 mt-3 ps-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.popularityFemale)" :resultTypes="resultsType.popularityFemale.resultTypes" :top="3"/>
          </div>
          <h5 class="col col-12 subsection-title mb-1">Biggest Differences in Popularity by Gender</h5>
          <p class="col col-12 text-center">Expressed as the ratio of male popularity to female popularity (and vice versa).</p>
          <div class="col col-6 mt-3 pe-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.popularityRatioMale)" :resultTypes="resultsType.popularityRatioMale.resultTypes" :top="3"/>
          </div>
          <div class="col col-6 mt-3 ps-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.popularityRatioFemale)" :resultTypes="resultsType.popularityRatioFemale.resultTypes" :top="3"/>
          </div>
        </div>
      </div>
    </div>

    <div class="row justify-content-center mt-4">
      <div class="col col-11">
        <div class="row">
          <button class="btn title-color w-100 collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapsable-popularity-miscellaneous" aria-expanded="false" aria-controls="collapsable-popularity-miscellaneous">
            <h4>
              <span class="show-if-collapsed">Show</span>
              <span class="show-if-not-collapsed">Hide</span>
              Popularity - Miscellaneous
            </h4>
          </button>
        </div>
        <div class="row collapse text-smaller border rounded" id="collapsable-popularity-miscellaneous">
          <template v-if="!surveyIsPreseason">
            <h5 class="col col-12 subsection-title mb-1">Most Underwatched Anime</h5>
            <div class="col-12">
              <TableWithTop3 :ranking="getRanking(resultsType.underwatched)" :resultTypes="resultsType.underwatched.resultTypes" :top="5"/>
            </div>
          </template>
          <h5 class="col col-12 subsection-title mb-1">Average Age per Anime</h5>
          <div class="col col-6 mt-3 pe-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.age)" :resultTypes="resultsType.age.resultTypes" :top="3"/>
          </div>
          <div class="col col-6 mt-3 ps-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.age, false, true)" :resultTypes="resultsType.age.resultTypes" :top="3"/>
          </div>
        </div>
      </div>
    </div>

    <h3 class="section-title">Impressions</h3>
    <h5 class="subsection-title">
      {{ surveyIsPreseason ? 'Most (and Least) Anticipated Anime of the Season' : 'Best (and Worst) Anime of the Season' }}
    </h5>
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.score)" :resultTypes="resultsType.score.resultTypes" :top="10"/> <!-- Bottom 5 -->

    <div class="row justify-content-center mt-4" v-if="!surveyIsPreseason">
      <div class="col col-11">
        <div class="row">
          <button class="btn title-color w-100 collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapsable-score-gender" aria-expanded="false" aria-controls="collapsable-score-gender">
            <h4>
              <span class="show-if-collapsed">Show</span>
              <span class="show-if-not-collapsed">Hide</span>
              Impressions - By Gender
            </h4>
          </button>
        </div>
        <div class="row collapse text-smaller border rounded" id="collapsable-score-gender">
          <h5 class="col col-12 subsection-title mb-1">Best Anime of the Season by Gender</h5>
          <div class="col col-6 mt-3 pe-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.scoreMale)" :resultTypes="resultsType.scoreMale.resultTypes" :top="5"/>
          </div>
          <div class="col col-6 mt-3 ps-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.scoreFemale)" :resultTypes="resultsType.scoreFemale.resultTypes" :top="5"/>
          </div>
          <h5 class="col col-12 subsection-title mb-1">Biggest Differences in Score by Gender</h5>
          <p class="col col-12 text-center">Expressed in how much higher an anime was scored by men compared to women (and vice versa).</p>
          <div class="col col-6 mt-3 pe-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.scoreDiffMale)" :resultTypes="resultsType.scoreDiffMale.resultTypes" :top="3"/>
          </div>
          <div class="col col-6 mt-3 ps-4">
            <SimpleResultsTable :ranking="getRanking(resultsType.scoreDiffFemale)" :resultTypes="resultsType.scoreDiffFemale.resultTypes" :top="3"/>
          </div>
        </div>
      </div>
    </div>

    <div class="row justify-content-center mt-4" v-if="!surveyIsPreseason">
      <div class="col col-11">
        <div class="row">
          <button class="btn title-color w-100 collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapsable-score-gender" aria-expanded="false" aria-controls="collapsable-score-gender">
            <h4>
              <span class="show-if-collapsed">Show</span>
              <span class="show-if-not-collapsed">Hide</span>
              Impressions - Expectations
            </h4>
          </button>
        </div>
        <div class="row collapse text-smaller border rounded" id="collapsable-score-gender">
          <h5 class="col col-12 subsection-title mb-1">Most Surprising Anime</h5>
          <div class="col-12">
            <TableWithTop3 :ranking="getRanking(resultsType.surprise)" :resultTypes="resultsType.surprise.resultTypes" :top="5"/>
          </div>
          <h5 class="col col-12 subsection-title mb-1">Most Disappointing Anime</h5>
          <div class="col-12">
            <TableWithTop3 :ranking="getRanking(resultsType.disappointment)" :resultTypes="resultsType.disappointment.resultTypes" :top="5"/>
          </div>
        </div>
      </div>
    </div>

    <h3 class="section-title">Anime OVAs / ONAs / Movies / Specials</h3>
    <h5 class="subsection-title">Most Popular Anime OVAs / ONAs / Movies / Specials</h5>
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.popularity, true)" :resultTypes="resultsType.popularity.resultTypes" :top="5"/>

    <h5 class="subsection-title">Best Anime OVAs / ONAs / Movies / Specials</h5>
    <TableWithTop3 class="mt-3" :ranking="getRanking(resultsType.score, true)" :resultTypes="resultsType.score.resultTypes" :top="5"/>
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

  // TODO: Super scuffed, please change how this works
  readonly resultsType: Record<string, { value: ResultsType, resultTypes: ResultsType[] }> = {
    popularity: { value: ResultsType.POPULARITY, resultTypes: [ResultsType.POPULARITY] },
    popularityMale: { value: ResultsType.POPULARITY_MALE, resultTypes: [ResultsType.POPULARITY_MALE, ResultsType.POPULARITY] },
    popularityFemale: { value: ResultsType.POPULARITY_FEMALE, resultTypes: [ResultsType.POPULARITY_FEMALE, ResultsType.POPULARITY] },
    popularityRatioMale: { value: ResultsType.GENDER_POPULARITY_RATIO, resultTypes: [ResultsType.GENDER_POPULARITY_RATIO, ResultsType.POPULARITY] },
    popularityRatioFemale: { value: ResultsType.GENDER_POPULARITY_RATIO_INV, resultTypes: [ResultsType.GENDER_POPULARITY_RATIO_INV, ResultsType.POPULARITY] },
    score: { value: ResultsType.SCORE, resultTypes: [ResultsType.SCORE] },
    scoreMale: { value: ResultsType.SCORE_MALE, resultTypes: [ResultsType.SCORE_MALE, ResultsType.SCORE] },
    scoreFemale: { value: ResultsType.SCORE_FEMALE, resultTypes: [ResultsType.SCORE_FEMALE, ResultsType.SCORE] },
    scoreDiffMale: { value: ResultsType.GENDER_SCORE_DIFFERENCE, resultTypes: [ResultsType.GENDER_SCORE_DIFFERENCE, ResultsType.SCORE] },
    scoreDiffFemale: { value: ResultsType.GENDER_SCORE_DIFFERENCE_INV, resultTypes: [ResultsType.GENDER_SCORE_DIFFERENCE_INV, ResultsType.SCORE] },
    age: { value: ResultsType.AGE, resultTypes: [ResultsType.AGE] },
    underwatched: { value: ResultsType.UNDERWATCHED, resultTypes: [ResultsType.UNDERWATCHED, ResultsType.POPULARITY] },
    surprise: { value: ResultsType.SURPRISE, resultTypes: [ResultsType.SURPRISE, ResultsType.SCORE] },
    disappointment: { value: ResultsType.DISAPPOINTMENT, resultTypes: [ResultsType.DISAPPOINTMENT, ResultsType.SCORE] },
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

  getRanking(resultsTypeData: { value: ResultsType, resultTypes: ResultsType[] }, forSpecialAnime = false, ascending = false): { anime: AnimeData, result: number, extraResult?: number }[] {
    let resultsTable: { anime: AnimeData, result: number, extraResult?: number }[] = [];

    const animeIds = Object.keys(this.surveyResultsData!.results);
    animeIds.forEach(animeIdStr => {
      const animeId = Number(animeIdStr);
      const animeData = this.surveyResultsData!.anime[animeId];
      if (isAnimeSeries(animeData) === forSpecialAnime) return;

      const extraResult: ResultsType|undefined = resultsTypeData.resultTypes[1];
      resultsTable.push({
        anime: animeData,
        result: this.surveyResultsData!.results[animeId][resultsTypeData.value],
        extraResult: extraResult ? this.surveyResultsData!.results[animeId][extraResult] : undefined,
      });
    });
    resultsTable = resultsTable.filter(item => item.result != null);
    resultsTable.sort((a, b) => a.result - b.result);

    if (!ascending) resultsTable.reverse();
    return resultsTable;
  }
}
</script>