<template>
  <div>
    <AnimeTable :columns="tableColumns" :entries="tableEntries"/>

    <router-link :to="{ name: 'SurveyResultsSummary' }">To results summary</router-link>
  </div>
</template>

<script lang="ts">
import { ResultsType } from '@/util/data';
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
  tableEntries: AnimeTableEntryData[] = [];

  created(): void {
    this.surveyResultsData = this.surveyResultsDataRef.value;

    for (const objectKey in ResultsType) {
      if (!isNaN(Number(objectKey))) continue; // Only get string keys
      const resultType = Number(ResultsType[objectKey]) as ResultsType;
      this.tableColumns.push(new AnimeTableColumnData(resultType));
    }
  }
}
</script>