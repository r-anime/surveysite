<template>
  <div>
    <h3 class="section-title">Anime Series</h3>
    <AnimeTable :columns="tableColumnsOfSeries" :entries="tableEntriesOfSeries"/>

    <h3 class="section-title">Anime OVAs / ONAs / Movies / Specials</h3>
    <AnimeTable :columns="tableColumnsOfSpecial" :entries="tableEntriesOfSpecial"/>

    <router-link :to="{ name: 'SurveyResultsSummary' }">To results summary</router-link>
  </div>
</template>

<script lang="ts">
import { ResultsType } from '@/util/data';
import { isAnimeSeries } from '@/util/helpers';
import { ComputedRef } from '@vue/reactivity';
import { Options, Vue } from 'vue-class-component';
import AnimeTable from './components/AnimeTable.vue';
import { AnimeTableColumnData } from './data/anime-table-column-data';
import { AnimeTableEntryData } from './data/anime-table-entry-data';
import { SurveyResultsData } from './data/survey-results-data';

@Options({
  components: {
    AnimeTable,
  },
  inject: [
    'surveyResultsDataRef',
  ],
})
export default class SurveyResultsFull extends Vue {
  surveyResultsDataRef!: ComputedRef<SurveyResultsData>;
  surveyResultsData?: SurveyResultsData;

  tableColumnsOfSeries: AnimeTableColumnData[] = [];
  tableColumnsOfSpecial: AnimeTableColumnData[] = [];
  tableEntriesOfSeries: AnimeTableEntryData[] = [];
  tableEntriesOfSpecial: AnimeTableEntryData[] = [];

  created(): void {
    this.surveyResultsData = this.surveyResultsDataRef.value;

    // Columns
    const resultTypesOfSeries: ResultsType[] = this.surveyResultsData.survey.isPreseason ? [
      ResultsType.POPULARITY,
      ResultsType.POPULARITY_MALE,
      ResultsType.POPULARITY_FEMALE,
      ResultsType.GENDER_POPULARITY_RATIO,
      ResultsType.AGE,
      ResultsType.SCORE,
      ResultsType.SCORE_MALE,
      ResultsType.SCORE_FEMALE,
      ResultsType.GENDER_SCORE_DIFFERENCE,
    ] : [
      ResultsType.POPULARITY,
      ResultsType.POPULARITY_MALE,
      ResultsType.POPULARITY_FEMALE,
      ResultsType.GENDER_POPULARITY_RATIO,
      ResultsType.AGE,
      ResultsType.UNDERWATCHED,
      ResultsType.SCORE,
      ResultsType.SCORE_MALE,
      ResultsType.SCORE_FEMALE,
      ResultsType.GENDER_SCORE_DIFFERENCE,
      ResultsType.SURPRISE,
      ResultsType.DISAPPOINTMENT,
    ];
    const resultTypesOfSpecial: ResultsType[] = this.surveyResultsData.survey.isPreseason ? [
      ResultsType.POPULARITY,
      ResultsType.POPULARITY_MALE,
      ResultsType.POPULARITY_FEMALE,
      ResultsType.GENDER_POPULARITY_RATIO,
      ResultsType.AGE,
    ] : [
      ResultsType.POPULARITY,
      ResultsType.POPULARITY_MALE,
      ResultsType.POPULARITY_FEMALE,
      ResultsType.GENDER_POPULARITY_RATIO,
      ResultsType.AGE,
      ResultsType.SCORE,
      ResultsType.SCORE_MALE,
      ResultsType.SCORE_FEMALE,
      ResultsType.GENDER_SCORE_DIFFERENCE,
    ];
    for (const resultType of resultTypesOfSeries) {
      this.tableColumnsOfSeries.push({
        resultType: resultType,
      });
    }
    for (const resultType of resultTypesOfSpecial) {
      this.tableColumnsOfSpecial.push({
        resultType: resultType,
      });
    }

    // Entries
    for (const animeIdStr in this.surveyResultsData.results) {
      const animeId = Number(animeIdStr);
      // TODO: Toggle for: if (this.surveyResultsData.results[animeId][ResultsType.POPULARITY] < 0.02) continue;

      const animeTableEntry: AnimeTableEntryData = {
        anime: this.surveyResultsData.anime[animeId],
        data: this.surveyResultsData.results[animeId],
      }

      if (isAnimeSeries(animeTableEntry.anime)) {
        this.tableEntriesOfSeries.push(animeTableEntry);
      } else {
        this.tableEntriesOfSpecial.push(animeTableEntry);
      }
    }
  }
}
</script>