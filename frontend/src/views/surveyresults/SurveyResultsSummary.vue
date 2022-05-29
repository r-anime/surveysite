<template>
  <div>
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
    <TableWithTop3
      :ranking="getRanking(resultType.popularity)"
      :resultTypes="resultType.popularity.resultTypes"
      isAnimeSeries
      :top="10"
      title="Most Popular Anime Series"
    />

    <div class="row justify-content-center mt-4">
      <div class="col-11">
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
          <div class="col-12">
            <TablePair
              :leftRanking="getRanking(resultType.popularityMale)"
              :leftResultTypes="resultType.popularityMale.resultTypes"
              :rightRanking="getRanking(resultType.popularityFemale)"
              :rightResultTypes="resultType.popularityFemale.resultTypes"
              isAnimeSeries
              title="Most Popular Anime Series by Gender"
              :top="3"
            />
          </div>
          <div class="col-12">
            <TablePair
              :leftRanking="getRanking(resultType.popularityRatio)"
              :leftResultTypes="resultType.popularityRatio.resultTypes"
              isAnimeSeries
              title="Biggest Differences in Popularity by Gender"
              description="Expressed as the ratio of male popularity to female popularity (and vice versa)."
              :top="3"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="row justify-content-center mt-4">
      <div class="col-11">
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
          <div class="col-12" v-if="!surveyIsPreseason">
            <TableWithTop3
              :ranking="getRanking(resultType.underwatched)"
              :resultTypes="resultType.underwatched.resultTypes"
              isAnimeSeries
              :top="5"
              title="Most Underwatched Anime"
            />
          </div>
          <div class="col-12">
            <TablePair
              :leftRanking="getRanking(resultType.age)"
              :leftResultTypes="resultType.age.resultTypes"
              isAnimeSeries
              title="Average Age per Anime"
              :top="3"
            />
          </div>
        </div>
      </div>
    </div>

    <h3 class="section-title">Impressions</h3>
    <TableWithTop3
      :ranking="getRanking(resultType.score)"
      :resultTypes="resultType.score.resultTypes"
      isAnimeSeries
      :top="10"
      :bottom="5"
      :title="surveyIsPreseason ? 'Most (and Least) Anticipated Anime of the Season' : 'Best (and Worst) Anime of the Season'"
    />

    <div class="row justify-content-center mt-4">
      <div class="col-11">
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
          <div class="col-12">
            <TablePair
              :leftRanking="getRanking(resultType.scoreMale)"
              :leftResultTypes="resultType.scoreMale.resultTypes"
              :rightRanking="getRanking(resultType.scoreFemale)"
              :rightResultTypes="resultType.scoreFemale.resultTypes"
              isAnimeSeries
              :title="surveyIsPreseason ? 'Most Anticipated Anime of the Season by Gender' : 'Best Anime of the Season by Gender'"
              :top="5"
            />
          </div>
          <div class="col-12">
            <TablePair
              :leftRanking="getRanking(resultType.scoreDiff)"
              :leftResultTypes="resultType.scoreDiff.resultTypes"
              isAnimeSeries
              title="Biggest Differences in Score by Gender"
              description="Expressed in how much higher an anime was scored by men compared to women (and vice versa)."
              :top="3"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="row justify-content-center mt-4" v-if="!surveyIsPreseason">
      <div class="col-11">
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
          <div class="col-12">
            <TableWithTop3
              :ranking="getRanking(resultType.surprise)"
              :resultTypes="resultType.surprise.resultTypes"
              isAnimeSeries
              :top="5"
              title="Most Surprising Anime"
            />
          </div>
          <div class="col-12">
            <TableWithTop3
              :ranking="getRanking(resultType.disappointment)"
              :resultTypes="resultType.disappointment.resultTypes"
              isAnimeSeries
              :top="5"
              title="Most Disappointing Anime"
            />
          </div>
        </div>
      </div>
    </div>

    <h3 class="section-title">Anime OVAs / ONAs / Movies / Specials</h3>
    <TableWithTop3
      :ranking="getRanking(resultType.popularity, true)"
      :resultTypes="resultType.popularity.resultTypes"
      :top="5"
      title="Most Popular Anime OVAs / ONAs / Movies / Specials"
    />

    <TableWithTop3
      v-if="!surveyIsPreseason"
      :ranking="getRanking(resultType.score, true)"
      :resultTypes="resultType.score.resultTypes"
      :top="5"
      title="Best Anime OVAs / ONAs / Movies / Specials"
    />

    <div class="row g-0">
      <div class="col-auto pe-1">
        <router-link :to="{ name: 'Index' }" class="btn btn-secondary">Back to index</router-link>
      </div>
      <div class="col"></div>
      <div class="col-auto ps-1">
        <router-link :to="{ name: 'SurveyResultsFull' }" class="btn btn-primary">To full results</router-link>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { AnimeData, ResultType } from '@/util/data';
import { isAnimeSeries } from '@/util/helpers';
import _ from 'lodash';
import { Vue, Options } from 'vue-class-component';
import AgeDistributionChart from './components/AgeDistributionChart.vue';
import GenderDistributionChart from './components/GenderDistributionChart.vue';
import TableWithTop3 from './components/TableWithTop3.vue';
import TablePair from './components/TablePair.vue';
import { SurveyResultsData } from './data/survey-results-data';

@Options({
  components: {
    AgeDistributionChart,
    GenderDistributionChart,
    TableWithTop3,
    TablePair,
    AnimeNames,
    AnimeImages,
  },
  inject: [
    'surveyResultsData',
  ],
})
export default class SurveyResultsSummary extends Vue {
  surveyResultsData!: SurveyResultsData;
  surveyIsPreseason = true;
  pageTitle?: string;
  averageAge?: string;

  // TODO: Super scuffed, please change how this works
  readonly resultType: Record<string, { value: ResultType, resultTypes: [ResultType] | [ResultType, ResultType] }> = {
    popularity: { value: ResultType.POPULARITY, resultTypes: [ResultType.POPULARITY] },
    popularityMale: { value: ResultType.POPULARITY_MALE, resultTypes: [ResultType.POPULARITY_MALE, ResultType.POPULARITY] },
    popularityFemale: { value: ResultType.POPULARITY_FEMALE, resultTypes: [ResultType.POPULARITY_FEMALE, ResultType.POPULARITY] },
    popularityRatio: { value: ResultType.GENDER_POPULARITY_RATIO, resultTypes: [ResultType.GENDER_POPULARITY_RATIO, ResultType.POPULARITY] },
    score: { value: ResultType.SCORE, resultTypes: [ResultType.SCORE] },
    scoreMale: { value: ResultType.SCORE_MALE, resultTypes: [ResultType.SCORE_MALE, ResultType.SCORE] },
    scoreFemale: { value: ResultType.SCORE_FEMALE, resultTypes: [ResultType.SCORE_FEMALE, ResultType.SCORE] },
    scoreDiff: { value: ResultType.GENDER_SCORE_DIFFERENCE, resultTypes: [ResultType.GENDER_SCORE_DIFFERENCE, ResultType.SCORE] },
    age: { value: ResultType.AGE, resultTypes: [ResultType.AGE] },
    underwatched: { value: ResultType.UNDERWATCHED, resultTypes: [ResultType.UNDERWATCHED, ResultType.POPULARITY] },
    surprise: { value: ResultType.SURPRISE, resultTypes: [ResultType.SURPRISE, ResultType.SCORE] },
    disappointment: { value: ResultType.DISAPPOINTMENT, resultTypes: [ResultType.DISAPPOINTMENT, ResultType.SCORE] },
  };

  created(): void {
    this.surveyIsPreseason = this.surveyResultsData.survey.isPreseason;
    this.averageAge = _.sum(
      Object.entries(this.surveyResultsData.miscellaneous.ageDistribution).map(([ageStr, percentage]) => Number(ageStr) * percentage / 100)
    ).toFixed(2);
  }

  getRanking(resultTypeData: { value: ResultType, resultTypes: [ResultType] | [ResultType, ResultType] }, forSpecialAnime = false, ascending = false): { anime: AnimeData, result: number, extraResult?: number }[] {
    let resultsTable: { anime: AnimeData, result: number, extraResult?: number }[] = [];

    const animeIds = Object.keys(this.surveyResultsData.results);
    animeIds.forEach(animeIdStr => {
      const animeId = Number(animeIdStr);
      if (this.surveyResultsData.results[animeId][ResultType.POPULARITY] < 0.02) return;

      const animeData = this.surveyResultsData.anime[animeId];
      if (isAnimeSeries(animeData) === forSpecialAnime) return;

      const mainResult = resultTypeData.resultTypes[0];
      const extraResult = resultTypeData.resultTypes[1];
      resultsTable.push({
        anime: animeData,
        result: this.surveyResultsData.results[animeId][mainResult],
        extraResult: extraResult ? this.surveyResultsData.results[animeId][extraResult] : undefined,
      });
    });
    resultsTable = resultsTable.filter(item => item.result != null);
    resultsTable.sort((a, b) => a.result - b.result);

    if (!ascending) resultsTable.reverse();
    return resultsTable;
  }
}
</script>