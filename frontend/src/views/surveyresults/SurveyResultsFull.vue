<template>
  <div>
    <div class="form-check">
      <input class="form-check-input" type="checkbox" v-model="filterBelowPopularityThreshold" id="filterBelowPopularityThreshold">
      <label class="form-check-label" for="filterBelowPopularityThreshold">Filter away anime below the popularity threshold (2%)</label>
    </div>
    <h3 class="section-title">Anime Series</h3>
    <div class="row row-cols-4">
      <div class="col form-check" v-for="column in tableDataOfSeries.columns" :key="`series${column.resultType}`">
        <input class="form-check-input" :id="`columnCheckboxSeries${column.resultType}`" type="checkbox" v-model="tableDataOfSeries.isColumnVisible[column.resultType]"/>
        <label class="form-check-label" :for="`columnCheckboxSeries${column.resultType}`">{{ getResultTypeName(column.resultType) }}</label>
      </div>
    </div>
    <FullResultsTable :columns="tableDataOfSeries.processedColumns" :entries="tableDataOfSeries.entries"/>

    <h3 class="section-title">Anime OVAs / ONAs / Movies / Specials</h3>
    <div class="row row-cols-4">
      <div class="col form-check" v-for="column in tableDataOfSpecial.columns" :key="`special${column.resultType}`">
        <input class="form-check-input" :id="`columnCheckboxSpecial${column.resultType}`" type="checkbox" v-model="tableDataOfSpecial.isColumnVisible[column.resultType]"/>
        <label class="form-check-label" :for="`columnCheckboxSpecial${column.resultType}`">{{ getResultTypeName(column.resultType) }}</label>
      </div>
    </div>
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
import { ResultsType } from '@/util/data';
import { getResultTypeName, isAnimeSeries } from '@/util/helpers';
import { ComputedRef } from '@vue/reactivity';
import { Options, Vue } from 'vue-class-component';
import FullResultsTable from './components/FullResultsTable.vue';
import { AnimeTableColumnData } from './data/anime-table-column-data';
import { AnimeTableEntryData } from './data/anime-table-entry-data';
import { SurveyResultsData } from './data/survey-results-data';

class TableData {
  columns: AnimeTableColumnData[] = [];
  entries: AnimeTableEntryData[] = [];
  isColumnVisible: Partial<Record<ResultsType, boolean>> = {};

  get processedColumns(): AnimeTableColumnData[] {
    return this.columns.filter(column => this.isColumnVisible[column.resultType]);
  }
}

@Options({
  components: {
    FullResultsTable,
  },
  inject: [
    'surveyResultsDataRef',
  ],
})
export default class SurveyResultsFull extends Vue {
  surveyResultsDataRef!: ComputedRef<SurveyResultsData>;
  surveyResultsData?: SurveyResultsData;

  tableDataOfSeries = new TableData();
  tableDataOfSpecial = new TableData();

  filterBelowPopularityThreshold = true;

  getResultTypeName = getResultTypeName;

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
      this.tableDataOfSeries.columns.push({ resultType });
      this.tableDataOfSeries.isColumnVisible[resultType] = true;
    }

    for (const resultType of resultTypesOfSpecial) {
      this.tableDataOfSpecial.columns.push({ resultType });
      this.tableDataOfSpecial.isColumnVisible[resultType] = true;
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
        if (filterEnabled && this.surveyResultsData.results[animeId][ResultsType.POPULARITY] < 0.02) continue;

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