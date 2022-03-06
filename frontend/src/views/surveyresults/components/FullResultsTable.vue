<template>
  <table role="table" :aria-colcount="3 + columns.length" class="table table-bordered">
    <thead role="rowgroup">
      <tr role="row">
        <th role="columnheader" scope="col" aria-colindex="1" class="table-col-rank align-middle" aria-label="Rank"></th>
        <th role="columnheader" scope="col" aria-colindex="2" colspan="2" :class="['table-col-anime', 'align-middle', 'clickable', 'table-col-sortable', getColumnSortCssClass(null)]" @click="sortByResultType(null)">Anime</th>
        <th v-for="(column, columnIdx) in processedColumns"
            :key="column.resultType"
            role="columnheader"
            scope="col"
            :aria-colindex="columnIdx + 4"
            :class="['table-col-result', 'align-middle', 'clickable', 'table-col-sortable', getColumnSortCssClass(column.resultType)]"
            :style="column.cssStyle"
            @click="sortByResultType(column.resultType)"
        >
          {{ getResultTypeName(column.resultType) }}
        </th>
      </tr>
    </thead>
    <tbody role="rowgroup">
      <tr role="row" v-for="(entry, entryIdx) in processedEntries" :key="entry.anime.id">
        <td role="cell" aria-colindex="1" class="table-col-rank">
          #{{ entryIdx + 1 }}
        </td>
        <td role="cell" aria-colindex="2" class="table-col-image border-end-0" style="height:5em;">
          <AnimeImages :animeImages="entry.anime.images" :enableCarouselControls="false" maxHeight="5em"/>
        </td>
        <td role="cell" aria-colindex="3" class="table-col-name border-start-0">
          <AnimeNames :animeNames="entry.anime.names"/>
        </td>
        <td role="cell" :aria-colindex="columnIdx + 4" class="table-col-result" v-for="(column, columnIdx) in processedColumns" :key="column.resultType">
          {{ getResultTypeFormatter(column.resultType)(entry.data[column.resultType]) }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import AnimeImages from '@/components/AnimeImages.vue';
import AnimeNames from '@/components/AnimeNames.vue';
import { getAnimeName, getResultTypeFormatter, getResultTypeName } from '@/util/helpers';
import { AnimeNameType, ResultsType } from '@/util/data';
import { AnimeTableEntryData } from '../data/anime-table-entry-data';
import _ from 'lodash';
import { AnimeTableColumnData } from '../data/anime-table-column-data';

@Options({
  props: {
    columns: Array,
    entries: Array,
    isAnimeSeries: Boolean,
  },
  components: {
    AnimeImages,
    AnimeNames,
  }
})
export default class FullResultsTable extends Vue {
  columns!: AnimeTableColumnData[];
  entries!: AnimeTableEntryData[];
  isAnimeSeries!: boolean;

  get processedColumns(): AnimeTableColumnData[] {
    return this.columns;
  }
  processedEntries: AnimeTableEntryData[] = this.entries;

  getResultTypeFormatter = getResultTypeFormatter;
  getResultTypeName = getResultTypeName;

  activeSort: {
    resultType: ResultsType | null,
    descending: boolean,
  } = {
    resultType: null,
    descending: true,
  }

  private get sortRouteQueryKey(): string {
    return this.isAnimeSeries ? 'sortSeries' : 'sortSpecial';
  }

  created(): void {
    const sortValueRaw = this.$route.query[this.sortRouteQueryKey];
    if (sortValueRaw && !Array.isArray(sortValueRaw)) {
      const sortValue: ResultsType = Number(sortValueRaw);
      this.sortByResultType(sortValue);
    } else {
      this.sortByResultType(null);
    }

    this.$watch(() => this.entries, (newEntries: AnimeTableEntryData[]) => {
      this.processedEntries = newEntries;
      this.activeSort.descending = !this.activeSort.descending; // Not exactly pretty, but prevent swapping the order
      this.sortByResultType(this.activeSort.resultType);
    });
  }

  /**
   * Sort columns by a particular result type
   * @param resultType Result type to sort by, or null to sort by (Japanese) name
   */
  sortByResultType(resultType: ResultsType | null): void {
    let descending = resultType != null; // When sorting by name, sort ascending first, otherwise descending
    if (this.activeSort.resultType == resultType) {
      descending = !this.activeSort.descending;
    }

    this.activeSort.resultType = resultType;
    this.activeSort.descending = descending;

    // Overwrite this sort query with the one currently in the route
    const newSortQuery = Object.assign({}, this.$route.query);
    if (resultType != null) {
      const query = { [this.sortRouteQueryKey]: resultType.toString() };
      Object.assign(newSortQuery, query);
    }
    else {
      if (newSortQuery[this.sortRouteQueryKey]) {
        delete newSortQuery[this.sortRouteQueryKey];
      }
    }
    this.$router.replace({ name: 'SurveyResultsFull', query: newSortQuery, hash: this.$route.hash });

    this.processedEntries = _.orderBy(this.processedEntries, entry => {
      if (resultType == null)
        return getAnimeName(entry.anime, AnimeNameType.JAPANESE_NAME)?.toLowerCase();
      else if (entry.data[resultType] == null || entry.data[resultType] === 0)
        return descending ? -1000 : 1000;
      else
        return entry.data[resultType];
    }, descending ? 'desc' : 'asc');
  }

  getColumnSortCssClass(resultType: ResultsType | null): Record<string, boolean> {
    const sortedOnColumn = this.activeSort.resultType === resultType;
    return {
      'table-col-sort-desc': sortedOnColumn && this.activeSort.descending,
      'table-col-sort-asc': sortedOnColumn && !this.activeSort.descending,
      'table-col-sort-none': !sortedOnColumn,
    };
  }
}
</script>

<style lang="scss" scoped>
@import "node_modules/bootstrap/scss/functions";
@import "node_modules/bootstrap/scss/variables";

.table-col-rank {
  width: 5%!important;
}
.table-col-anime {
  width: 33%!important; // image + name, 25 + 8
}
.table-col-image {
  width: 8%!important;
}
.table-col-name {
  width: 25%!important;
  position: relative!important;
}
.table-col-result {
  text-align: right!important;
  width: auto!important;
}

.table-col-sortable {
  $sort-icon-width: 0.6rem;
  $height-multiplier: 1.53;

  background-position: right center;
  background-repeat: no-repeat;
  background-size: $sort-icon-width $sort-icon-width*$height-multiplier;
  padding-right: $table-cell-padding-x + $sort-icon-width;
}

.table-col-sort-none {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='101' height='101' view-box='0 0 101 101' preserveAspectRatio='none'><path fill='black' opacity='.3' d='M51 1l25 23 24 22H1l25-22zM51 101l25-23 24-22H1l25 22z'/></svg>");
}
.table-col-sort-asc {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='101' height='101' view-box='0 0 101 101' preserveAspectRatio='none'><path fill='black' d='M51 1l25 23 24 22H1l25-22z'/><path fill='black' opacity='.3' d='M51 101l25-23 24-22H1l25 22z'/></svg>");
}
.table-col-sort-desc {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='101' height='101' view-box='0 0 101 101' preserveAspectRatio='none'><path fill='black' opacity='.3' d='M51 1l25 23 24 22H1l25-22z'/><path fill='black' d='M51 101l25-23 24-22H1l25 22z'/></svg>");
}

td {
  vertical-align: middle;
}
</style>