<template>
  <table role="table" :aria-colcount="3 + columns.length" class="table table-hover table-borderless">
    <thead role="rowgroup">
      <tr role="row">
        <th role="columnheader" scope="col" aria-colindex="1" class="table-col-rank" aria-label="Rank"></th>
        <th role="columnheader" scope="col" aria-colindex="2" class="table-col-image" aria-label="Image"></th>
        <th role="columnheader" scope="col" aria-colindex="3" class="table-col-name">Anime</th>
        <th role="columnheader" scope="col" :aria-colindex="columnIdx + 4" :class="column.cssClass" :style="column.cssStyle" v-for="(column, columnIdx) in columns" :key="columnIdx">{{ column.resultType }}</th>
      </tr>
    </thead>
    <tbody role="rowgroup">
      <tr role="row" v-for="(entry, entryIdx) in entries" :key="entryIdx">
        <td role="cell" aria-colindex="1" class="table-col-rank">
          #{{ idx + 1 }}
        </td>
        <td role="cell" aria-colindex="2" class="table-col-image" style="height:7.5em;">
          <AnimeImages :animeImages="entry.anime.images" :enableCarouselControls="false" maxHeight="7.5em"/>
        </td>
        <td role="cell" aria-colindex="3" class="table-col-name">
          <div class="mx-2">
            <AnimeNames :animeNames="entry.anime.names" :showShortName="false"/>
          </div>
        </td>
        <td role="cell" :aria-colindex="columnIdx + 4" :class="column.cssClass" :style="column.cssStyle" v-for="(column, columnIdx) in columns" :key="columnIdx">
          {{ entry.getResultValue(column.resultType) }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { ResultsType } from '@/util/data';
import { Options, Vue } from 'vue-class-component';
import AnimeImages from '@/components/AnimeImages.vue';
import AnimeNames from '@/components/AnimeNames.vue';
import { AnimeTableColumnData } from '../data/anime-table-column-data';
import { AnimeTableEntryData } from '../data/anime-table-entry-data';

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

  private readonly invalidValue = 'N/A';

  formatTableEntryData(data: AnimeTableEntryData['data'][0]): string {
    if (!data.value) return this.invalidValue;

    switch (data.resultType) {
      case ResultsType.POPULARITY:
      case ResultsType.POPULARITY_MALE:
      case ResultsType.POPULARITY_FEMALE:
      case ResultsType.SURPRISE:
      case ResultsType.DISAPPOINTMENT:
      case ResultsType.UNDERWATCHED:
        return this.percentageFormatter(data.value);
      case ResultsType.SCORE:
      case ResultsType.SCORE_MALE:
      case ResultsType.SCORE_FEMALE:
      case ResultsType.AGE:
        return this.numberFormatter(data.value);
      case ResultsType.GENDER_POPULARITY_RATIO:
        return this.genderRatioFormatter(data.value);
      case ResultsType.GENDER_SCORE_DIFFERENCE:
        return this.scoreDiffFormatter(data.value);
      default:
        return data.value.toString();
    }
  }

  // TODO: Put in a seperate file and reuse for SimpleResultsTable
  private percentageFormatter(value: number): string {
    return (value * 100).toFixed(1) + '%';
  }

  private genderRatioFormatter(value: number): string {
    const shouldInvert = value < 1;
    if (shouldInvert && value === 0) return this.invalidValue;
    return (shouldInvert ? 1 / value : value).toFixed(2) + ' ' + (shouldInvert ? 'F:M' : 'M:F');
  }

  private numberFormatter(value: number): string {
    return value.toFixed(2);
  }

  private scoreDiffFormatter(value: number): string {
    const shouldInvert = value < 0;
    return (shouldInvert ? -value : value).toFixed(2) + ' ' + (shouldInvert ? 'F' : 'M');
  }
}
</script>

<style lang="scss" scoped>
.table-col-rank {
  width: 5%!important;
}
.table-col-image {
  width: 15%!important;
}
.table-col-name {
  width: auto!important;
  position: relative!important;
}

td {
  vertical-align: middle;
}
</style>