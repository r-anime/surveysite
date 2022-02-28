<template>
  <table role="table" :aria-colcount="3 + columns.length" class="table table-hover">
    <thead role="rowgroup">
      <tr role="row">
        <th role="columnheader" scope="col" aria-colindex="1" class="table-col-rank align-middle" aria-label="Rank"></th>
        <th role="columnheader" scope="col" aria-colindex="2" class="table-col-image align-middle" aria-label="Image"></th>
        <th role="columnheader" scope="col" aria-colindex="3" :class="['table-col-name', 'align-middle', 'clickable', 'table-col-sortable', getColumnSortCssClass(null)]" @click="sortByResultType(null)">Anime</th>
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
        <td role="cell" aria-colindex="2" class="table-col-image" style="height:5em;">
          <AnimeImages :animeImages="entry.anime.images" :enableCarouselControls="false" maxHeight="5em"/>
        </td>
        <td role="cell" aria-colindex="3" class="table-col-name">
          <div class="mx-2">
            <AnimeNames :animeNames="entry.anime.names" :showShortName="false"/>
          </div>
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
  // Works, creates a new array
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
    this.$route.query[this.sortRouteQueryKey] = resultType != null ? resultType.toString() : null;

    this.processedEntries = _.orderBy(this.processedEntries, entry => {
      if (resultType == null)
        return getAnimeName(entry.anime, AnimeNameType.JAPANESE_NAME);
      else if (entry.data[resultType] == null || entry.data[resultType] === 0)
        return descending ? -1000 : 1000;
      else
        return entry.data[resultType];
    }, descending ? 'desc' : 'asc');
  }

  getColumnSortCssClass(resultType: ResultsType | null): Record<string, boolean> {
    const sortedOnColumn = this.activeSort.resultType === resultType;
    const sortTypeIsName = resultType == null;
    return {
      'table-col-sort-desc': sortedOnColumn && !sortTypeIsName && this.activeSort.descending,
      'table-col-sort-asc': sortedOnColumn && !sortTypeIsName && !this.activeSort.descending,
      'table-col-sort-name-desc': sortedOnColumn && sortTypeIsName && this.activeSort.descending,
      'table-col-sort-name-asc': sortedOnColumn && sortTypeIsName && !this.activeSort.descending,
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
  $sort-icon-width: 0.8rem;

  background-position: right center;
  background-repeat: no-repeat;
  background-size: $sort-icon-width;
  padding-right: $table-cell-padding-x + $sort-icon-width;
}

.table-col-sort-none {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' fill-opacity='0.5' class='bi bi-arrow-down-up' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M11.5 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L11 2.707V14.5a.5.5 0 0 0 .5.5zm-7-14a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L4 13.293V1.5a.5.5 0 0 1 .5-.5z'/></svg>");
}
.table-col-sort-asc {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-up' viewBox='0 0 16 16'><path d='M3.5 12.5a.5.5 0 0 1-1 0V3.707L1.354 4.854a.5.5 0 1 1-.708-.708l2-1.999.007-.007a.498.498 0 0 1 .7.006l2 2a.5.5 0 1 1-.707.708L3.5 3.707V12.5zm3.5-9a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zM7.5 6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zm0 3a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1h-3zm0 3a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1z'/></svg>");
}
.table-col-sort-desc {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-down' viewBox='0 0 16 16'><path d='M3.5 2.5a.5.5 0 0 0-1 0v8.793l-1.146-1.147a.5.5 0 0 0-.708.708l2 1.999.007.007a.497.497 0 0 0 .7-.006l2-2a.5.5 0 0 0-.707-.708L3.5 11.293V2.5zm3.5 1a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zM7.5 6a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1h-5zm0 3a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1h-3zm0 3a.5.5 0 0 0 0 1h1a.5.5 0 0 0 0-1h-1z'/></svg>");
}
.table-col-sort-name-asc {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-alpha-down' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M10.082 5.629 9.664 7H8.598l1.789-5.332h1.234L13.402 7h-1.12l-.419-1.371h-1.781zm1.57-.785L11 2.687h-.047l-.652 2.157h1.351z'/><path d='M12.96 14H9.028v-.691l2.579-3.72v-.054H9.098v-.867h3.785v.691l-2.567 3.72v.054h2.645V14zM4.5 2.5a.5.5 0 0 0-1 0v9.793l-1.146-1.147a.5.5 0 0 0-.708.708l2 1.999.007.007a.497.497 0 0 0 .7-.006l2-2a.5.5 0 0 0-.707-.708L4.5 12.293V2.5z'/></svg>");
}
.table-col-sort-name-desc {
  background-image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-sort-alpha-up-alt' viewBox='0 0 16 16'><path d='M12.96 7H9.028v-.691l2.579-3.72v-.054H9.098v-.867h3.785v.691l-2.567 3.72v.054h2.645V7z'/><path fill-rule='evenodd' d='M10.082 12.629 9.664 14H8.598l1.789-5.332h1.234L13.402 14h-1.12l-.419-1.371h-1.781zm1.57-.785L11 9.688h-.047l-.652 2.156h1.351z'/><path d='M4.5 13.5a.5.5 0 0 1-1 0V3.707L2.354 4.854a.5.5 0 1 1-.708-.708l2-1.999.007-.007a.498.498 0 0 1 .7.006l2 2a.5.5 0 1 1-.707.708L4.5 3.707V13.5z'/></svg>");
}

td {
  vertical-align: middle;
}
</style>