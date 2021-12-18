<template>
  <div>
    <h3 class="section-title">Anime Series</h3>
    <AnimeTable :columns="tableColumns" :entries="tableEntriesOfSeries"/>

    <h3 class="section-title">Anime OVAs / ONAs / Movies / Specials</h3>
    <AnimeTable :columns="tableColumns" :entries="tableEntriesOfSpecial"/>

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

  tableColumns: AnimeTableColumnData[] = [];
  tableEntriesOfSeries: AnimeTableEntryData[] = [];
  tableEntriesOfSpecial: AnimeTableEntryData[] = [];

  created(): void {
    this.surveyResultsData = this.surveyResultsDataRef.value;

    for (const objectKey in ResultsType) {
      if (!isNaN(Number(objectKey))) continue; // Only get string keys
      const resultType = Number(ResultsType[objectKey]) as ResultsType;
      this.tableColumns.push({
        resultType: resultType,
      });
    }

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