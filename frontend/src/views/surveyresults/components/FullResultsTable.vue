<template>
  <div class="table-responsive">
    <table role="table" :aria-colcount="3 + columns.length" class="table table-bordered">
      <thead role="rowgroup">
        <tr role="row">
          <th role="columnheader" scope="col" aria-colindex="1" class="table-col-rank align-middle" aria-label="Rank"></th>
          <th role="columnheader" scope="col" aria-colindex="2" colspan="2" :class="['table-col-anime', 'align-middle', 'clickable', 'table-col-sortable', getColumnSortCssClass(null)]" @click="sortByResultType(null)">Anime</th>
          <th v-for="(column, columnIdx) in columns"
              :key="column.resultType"
              role="columnheader"
              scope="col"
              :aria-colindex="columnIdx + 4"
              :class="['table-col-result', 'align-middle', 'clickable', 'table-col-sortable', getColumnSortCssClass(column.resultType)]"
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
            <AnimeImagesComponent :animeImages="entry.anime.images" maxHeight="5em"/>
          </td>
          <td role="cell" aria-colindex="3" class="table-col-name border-start-0">
            <AnimeNamesComponent :animeNames="entry.anime.names"/>
          </td>
          <td role="cell" :aria-colindex="columnIdx + 4" class="table-col-result" v-for="(column, columnIdx) in columns" :key="column.resultType">
            {{ getResultTypeFormatter(column.resultType)(entry.data[column.resultType]) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import AnimeImagesComponent from '@/components/AnimeImagesComponent.vue';
import AnimeNamesComponent from '@/components/AnimeNamesComponent.vue';
import { getAnimeName, getResultTypeFormatter, getResultTypeName } from '@/util/helpers';
import { AnimeNameType, ResultType } from '@/util/data';
import type { AnimeTableEntryData } from '../data/anime-table-entry-data';
import { orderBy } from 'lodash-es';
import type { AnimeTableColumnData } from '../data/anime-table-column-data';
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  columns: AnimeTableColumnData[];
  entries: AnimeTableEntryData[];
  isAnimeSeries?: boolean;
}>();

const sortRouteQueryKey = props.isAnimeSeries ? 'sortSeries' : 'sortSpecial';

const processedEntries = ref<AnimeTableEntryData[]>(props.entries);

const activeSort = ref<{
  resultType: ResultType | null,
  descending: boolean,
}>({
  resultType: null,
  descending: true,
});

const router = useRouter();
const route = router.currentRoute;


{
  const sortValueRaw = route.value.query[sortRouteQueryKey];
  if (sortValueRaw && !Array.isArray(sortValueRaw)) {
    const sortValue: ResultType = Number(sortValueRaw);
    sortByResultType(sortValue);
  } else {
    sortByResultType(null);
  }

  watch(() => props.entries, (newEntries: AnimeTableEntryData[]) => {
    processedEntries.value = newEntries;
    sortByResultType(activeSort.value.resultType, true);
  });
}



/**
 * Sort columns by a particular result type
 * @param resultType Result type to sort by, or null to sort by (Japanese) name
 */
function sortByResultType(resultType: ResultType | null, preventSortOrderToggle = false): void {
  const sameResultType = activeSort.value.resultType === resultType;
  const descending = sameResultType
    ? preventSortOrderToggle
      ? activeSort.value.descending  // Keep same order if preventSortOrderToggle,
      : !activeSort.value.descending // otherwise toggle it
    : resultType != null; // Start sorting in descending order, except when sorting by name

  activeSort.value.resultType = resultType;
  activeSort.value.descending = descending;

  // Overwrite the sort query currently in the route
  const newSortQuery = Object.assign({}, route.value.query);
  if (resultType != null) {
    const query = { [sortRouteQueryKey]: resultType.toString() };
    Object.assign(newSortQuery, query);
  }
  else {
    if (newSortQuery[sortRouteQueryKey]) {
      delete newSortQuery[sortRouteQueryKey];
    }
  }
  router.replace({ name: 'SurveyResultsFull', query: newSortQuery, hash: route.value.hash });

  processedEntries.value = orderBy(processedEntries.value, entry => {
    if (resultType == null)
      return getAnimeName(entry.anime, AnimeNameType.JAPANESE_NAME)?.toLowerCase();
    else if (entry.data[resultType] == null || entry.data[resultType] === 0)
      return descending ? -1000 : 1000;
    else
      return entry.data[resultType];
  }, descending ? 'desc' : 'asc');
}

function getColumnSortCssClass(resultType: ResultType | null): Record<string, boolean> {
  const sortedOnColumn = activeSort.value.resultType === resultType;
  return {
    'table-col-sort-desc': sortedOnColumn && activeSort.value.descending,
    'table-col-sort-asc': sortedOnColumn && !activeSort.value.descending,
    'table-col-sort-none': !sortedOnColumn,
  };
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