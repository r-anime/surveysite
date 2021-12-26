<template>
  <table role="table" :aria-colcount="3 + columns.length" class="table table-hover">
    <thead role="rowgroup">
      <tr role="row">
        <th role="columnheader" scope="col" aria-colindex="1" class="table-col-rank" aria-label="Rank"></th>
        <th role="columnheader" scope="col" aria-colindex="2" class="table-col-image" aria-label="Image"></th>
        <th role="columnheader" scope="col" aria-colindex="3" class="table-col-name clickable" @click="sortByResultType(null)">Anime</th>
        <th v-for="(column, columnIdx) in processedColumns"
            :key="column.resultType"
            role="columnheader"
            scope="col"
            :aria-colindex="columnIdx + 4"
            class="table-col-result clickable"
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
  },
  components: {
    AnimeImages,
    AnimeNames,
  }
})
export default class AnimeTable extends Vue {
  columns!: AnimeTableColumnData[];
  entries!: AnimeTableEntryData[];

  get processedColumns(): AnimeTableColumnData[] {
    return this.columns;
  }
  // Works, creates a new array as props are getters
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

  created(): void {
    this.sortByResultType(null);

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

    this.processedEntries = _.orderBy(this.processedEntries, entry => {
      if (resultType == null)
        return getAnimeName(entry.anime, AnimeNameType.JAPANESE_NAME);
      else if (entry.data[resultType] == null || entry.data[resultType] === 0)
        return descending ? -1000 : 1000;
      else
        return entry.data[resultType];
    }, descending ? 'desc' : 'asc');
  }
}
</script>

<style lang="scss" scoped>
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

td {
  vertical-align: middle;
}
</style>