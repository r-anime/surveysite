<template>
  <div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" v-model="filterBelowPopularityThreshold" id="filterBelowPopularityThreshold">
      <label class="form-check-label" for="filterBelowPopularityThreshold">Filter away anime below the popularity threshold (2%)</label>
    </div>
    <h3 class="section-title" id="tableSeries">Anime Series</h3>
    <DropdownMultiSelectComponent :items="tableDataOfSeries.columnsAsSelectorItems" v-model="tableDataOfSeries.visibleColumnTypes">
      Columns
    </DropdownMultiSelectComponent>
    <FullResultsTableComponent :columns="tableDataOfSeries.processedColumns" :entries="tableDataOfSeries.entries" isAnimeSeries/>

    <h3 class="section-title" id="tableSpecial">Anime OVAs / ONAs / Movies / Specials</h3>
    <DropdownMultiSelectComponent :items="tableDataOfSpecial.columnsAsSelectorItems" v-model="tableDataOfSpecial.visibleColumnTypes">
      Columns
    </DropdownMultiSelectComponent>
    <FullResultsTableComponent :columns="tableDataOfSpecial.processedColumns" :entries="tableDataOfSpecial.entries"/>

    <div class="row g-0">
      <div class="col-auto pe-1">
        <router-link :to="{ name: 'Index' }" class="btn btn-secondary">Back to index</router-link>
      </div>
      <div class="col-auto px-1">
        <router-link :to="{ name: 'SurveyResultsSummary' }" class="btn btn-secondary">Back to results summary</router-link>
      </div>
      <div class="col"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DropdownMultiSelectComponent from '@/components/DropdownMultiSelectComponent.vue';
import { ResultType, type SelectorItem } from '@/util/data';
import { getResultTypeName, isAnimeSeries } from '@/util/helpers';
import { inject, ref, watch, type Ref } from 'vue';
import FullResultsTableComponent from './components/FullResultsTableComponent.vue';
import type { AnimeTableColumnData } from './data/anime-table-column-data';
import type { AnimeTableEntryData } from './data/anime-table-entry-data';
import type { SurveyResultsData } from './data/survey-results-data';

class TableData {
  columns: AnimeTableColumnData[] = [];
  entries: AnimeTableEntryData[] = [];
  isColumnVisible: Partial<Record<ResultType, boolean>> = {};

  get processedColumns(): AnimeTableColumnData[] {
    return this.columns.filter(column => this.isColumnVisible[column.resultType]);
  }

  get columnsAsSelectorItems(): SelectorItem[] {
    return this.columns.map(column => ({ id: column.resultType, name: getResultTypeName(column.resultType, true) }));
  }

  get visibleColumnTypes(): ResultType[] {
    return this.processedColumns.map(column => column.resultType);
  }
  set visibleColumnTypes(value: ResultType[]) {
    this.columns.forEach(column => this.isColumnVisible[column.resultType] = value.includes(column.resultType));
  }
}



const surveyResultsData = inject<Ref<SurveyResultsData>>('surveyResultsData');
if (surveyResultsData == null) {
  throw new TypeError('Failed to inject surveyResultsData');
}

const tableDataOfSeries = ref(new TableData());
const tableDataOfSpecial = ref(new TableData());

const filterBelowPopularityThreshold = ref(true);



{
  // Columns
  const resultTypesOfSeries: { resultType: ResultType, priority: number }[] = surveyResultsData.value.survey.isPreseason ? [
    { resultType: ResultType.POPULARITY, priority: 1 },
    { resultType: ResultType.POPULARITY_MALE, priority: 3 },
    { resultType: ResultType.POPULARITY_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_POPULARITY_RATIO, priority: 2 },
    { resultType: ResultType.AGE, priority: 3 },
    { resultType: ResultType.SCORE, priority: 1 },
    { resultType: ResultType.SCORE_MALE, priority: 3 },
    { resultType: ResultType.SCORE_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_SCORE_DIFFERENCE, priority: 2 },
  ] : [
    { resultType: ResultType.POPULARITY, priority: 1 },
    { resultType: ResultType.POPULARITY_MALE, priority: 3 },
    { resultType: ResultType.POPULARITY_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_POPULARITY_RATIO, priority: 2 },
    { resultType: ResultType.AGE, priority: 3 },
    { resultType: ResultType.UNDERWATCHED, priority: 1 },
    { resultType: ResultType.SCORE, priority: 1 },
    { resultType: ResultType.SCORE_MALE, priority: 3 },
    { resultType: ResultType.SCORE_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_SCORE_DIFFERENCE, priority: 2 },
    { resultType: ResultType.SURPRISE, priority: 1 },
    { resultType: ResultType.DISAPPOINTMENT, priority: 1 },
  ];
  const resultTypesOfSpecial: { resultType: ResultType, priority: number }[] = surveyResultsData.value.survey.isPreseason ? [
    { resultType: ResultType.POPULARITY, priority: 1 },
    { resultType: ResultType.POPULARITY_MALE, priority: 3 },
    { resultType: ResultType.POPULARITY_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_POPULARITY_RATIO, priority: 2 },
    { resultType: ResultType.AGE, priority: 3 },
  ] : [
    { resultType: ResultType.POPULARITY, priority: 1 },
    { resultType: ResultType.POPULARITY_MALE, priority: 3 },
    { resultType: ResultType.POPULARITY_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_POPULARITY_RATIO, priority: 2 },
    { resultType: ResultType.AGE, priority: 3 },
    { resultType: ResultType.SCORE, priority: 1 },
    { resultType: ResultType.SCORE_MALE, priority: 3 },
    { resultType: ResultType.SCORE_FEMALE, priority: 3 },
    { resultType: ResultType.GENDER_SCORE_DIFFERENCE, priority: 2 },
  ];

  // By default we'll only show columns with a priority number <=2 for desktops/large screens, or <=1 for phones/small screens.
  // Breakpoint is 768 - Bootstrap's md breakpoint.
  const priority = window.innerWidth < 768 ? 1 : 2;
  for (const resultType of resultTypesOfSeries) {
    tableDataOfSeries.value.columns.push({ resultType: resultType.resultType });
    tableDataOfSeries.value.isColumnVisible[resultType.resultType] = resultType.priority <= priority;
  }

  for (const resultType of resultTypesOfSpecial) {
    tableDataOfSpecial.value.columns.push({ resultType: resultType.resultType });
    tableDataOfSpecial.value.isColumnVisible[resultType.resultType] = resultType.priority <= priority;
  }

  // Entries
  watch(filterBelowPopularityThreshold, filterEnabled => {
    if (!surveyResultsData?.value) {
      return;
    }

    tableDataOfSeries.value.entries = [];
    tableDataOfSpecial.value.entries = [];

    for (const animeIdStr in surveyResultsData.value.results) {
      const animeId = Number(animeIdStr);
      if (filterEnabled && surveyResultsData.value.results[animeId][ResultType.POPULARITY] < 0.02) continue;

      const animeTableEntry: AnimeTableEntryData = {
        anime: surveyResultsData.value.anime[animeId],
        data: surveyResultsData.value.results[animeId],
      };

      if (isAnimeSeries(animeTableEntry.anime)) {
        tableDataOfSeries.value.entries.push(animeTableEntry);
      } else {
        tableDataOfSpecial.value.entries.push(animeTableEntry);
      }
    }
  }, {
    immediate: true,
  });
}
</script>