<template>
  <table role="table" :aria-colcount="3 + columns.length" class="table table-hover">
    <thead role="rowgroup">
      <tr role="row">
        <th role="columnheader" scope="col" aria-colindex="1" class="table-col-rank" aria-label="Rank"></th>
        <th role="columnheader" scope="col" aria-colindex="2" class="table-col-image" aria-label="Image"></th>
        <th role="columnheader" scope="col" aria-colindex="3" class="table-col-name">Anime</th>
        <th role="columnheader" scope="col" :aria-colindex="columnIdx + 4" :class="column.cssClass" :style="column.cssStyle" v-for="(column, columnIdx) in columns" :key="columnIdx">{{ getResultTypeName(column.resultType) }}</th>
      </tr>
    </thead>
    <tbody role="rowgroup">
      <tr role="row" v-for="(entry, entryIdx) in entries" :key="entryIdx">
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
        <td role="cell" :aria-colindex="columnIdx + 4" :class="column.cssClass" :style="column.cssStyle" v-for="(column, columnIdx) in columns" :key="columnIdx">
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
import { getResultTypeFormatter, getResultTypeName } from '@/util/helpers';

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
  getResultTypeFormatter = getResultTypeFormatter;
  getResultTypeName = getResultTypeName;
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
  width: auto!important;
  position: relative!important;
}

td {
  vertical-align: middle;
}
</style>