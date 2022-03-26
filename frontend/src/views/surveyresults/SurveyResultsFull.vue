<template>
  <div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" v-model="filterBelowPopularityThreshold" id="filterBelowPopularityThreshold">
      <label class="form-check-label" for="filterBelowPopularityThreshold">Filter away anime below the popularity threshold (2%)</label>
    </div>
    <h3 class="section-title" id="tableSeries">Anime Series</h3>
    <DropdownMultiSelect :items="tableDataOfSeries.columnsAsSelectorItems" v-model="tableDataOfSeries.visibleColumnTypes">
      Columns
    </DropdownMultiSelect>
    <FullResultsTable :columns="tableDataOfSeries.processedColumns" :entries="tableDataOfSeries.entries" isAnimeSeries/>

    <h3 class="section-title" id="tableSpecial">Anime OVAs / ONAs / Movies / Specials</h3>
    <DropdownMultiSelect :items="tableDataOfSpecial.columnsAsSelectorItems" v-model="tableDataOfSpecial.visibleColumnTypes">
      Columns
    </DropdownMultiSelect>
    <FullResultsTable :columns="tableDataOfSpecial.processedColumns" :entries="tableDataOfSpecial.entries"/>

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

<script lang="ts">
import DropdownMultiSelect from '@/components/DropdownMultiSelect.vue';
import { ResultType, SelectorItem } from '@/util/data';
import { getResultTypeName, isAnimeSeries } from '@/util/helpers';
import { Options, Vue } from 'vue-class-component';
import FullResultsTable from './components/FullResultsTable.vue';
import { AnimeTableColumnData } from './data/anime-table-column-data';
import { AnimeTableEntryData } from './data/anime-table-entry-data';
import { SurveyResultsData } from './data/survey-results-data';

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

@Options({
  components: {
    FullResultsTable,
    DropdownMultiSelect,
  },
  inject: [
    'surveyResultsData',
  ],
})
export default class SurveyResultsFull extends Vue {
  surveyResultsData!: SurveyResultsData;

  tableDataOfSeries = new TableData();
  tableDataOfSpecial = new TableData();

  filterBelowPopularityThreshold = true;

  created(): void {
    // Columns
    const resultTypesOfSeries: { resultType: ResultType, priority: number }[] = this.surveyResultsData.survey.isPreseason ? [
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
    const resultTypesOfSpecial: { resultType: ResultType, priority: number }[] = this.surveyResultsData.survey.isPreseason ? [
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
      this.tableDataOfSeries.columns.push({ resultType: resultType.resultType });
      this.tableDataOfSeries.isColumnVisible[resultType.resultType] = resultType.priority <= priority;
    }

    for (const resultType of resultTypesOfSpecial) {
      this.tableDataOfSpecial.columns.push({ resultType: resultType.resultType });
      this.tableDataOfSpecial.isColumnVisible[resultType.resultType] = resultType.priority <= priority;
    }

    // Entries
    this.$watch(() => this.filterBelowPopularityThreshold, (filterEnabled: boolean) => {
      if (!this.surveyResultsData) {
        return;
      }

      this.tableDataOfSeries.entries = [];
      this.tableDataOfSpecial.entries = [];

      for (const animeIdStr in this.surveyResultsData.results) {
        const animeId = Number(animeIdStr);
        if (filterEnabled && this.surveyResultsData.results[animeId][ResultType.POPULARITY] < 0.02) continue;

        const animeTableEntry: AnimeTableEntryData = {
          anime: this.surveyResultsData.anime[animeId],
          data: this.surveyResultsData.results[animeId],
        }

        if (isAnimeSeries(animeTableEntry.anime)) {
          this.tableDataOfSeries.entries.push(animeTableEntry);
        } else {
          this.tableDataOfSpecial.entries.push(animeTableEntry);
        }
      }
    }, {
      immediate: true,
    });
  }
}
</script>