<template>
  <div class="mb-2">
    <table role="table" :aria-colcount="3 + resultNames.length" class="table table-hover table-borderless mb-0">
      <thead role="rowgroup">
        <tr role="row">
          <th role="columnheader" scope="col" aria-colindex="1" aria-label="Rank" class="table-col-rank"></th>
          <th role="columnheader" scope="col" aria-colindex="2" aria-label="Image" class="table-col-image"></th>
          <th role="columnheader" scope="col" aria-colindex="3" class="table-col-name">Anime</th>
          <th role="columnheader" scope="col" aria-colindex="4" class="table-col-main">{{ resultNames[0] }}</th>
          <th role="columnheader" scope="col" aria-colindex="5" class="table-col-extra" v-if="hasExtraResult">{{ resultNames[1] }}</th>
        </tr>
      </thead>
      <tbody role="rowgroup">
        <tr role="row" v-for="animeResult in processedRanking" :key="animeResult?.rank ?? -1">
          <td role="cell" aria-colindex="1" class="table-col-rank">
            {{ animeResult ? `#${animeResult.rank}` : '' }}
          </td>
          <td role="cell" aria-colindex="2" class="table-col-image" :style="animeResult ? { 'height': '7.5em' } : {}">
            <AnimeImages v-if="animeResult" :animeImages="animeResult.anime.images" :enableCarouselControls="false" maxHeight="7.5em"/>
          </td>
          <td role="cell" aria-colindex="3" class="table-col-name">
            <template v-if="animeResult">
              <div class="mx-2">
                <AnimeNames :animeNames="animeResult.anime.names" showShortName/>
              </div>
              <div class="progress-bar table-row-progress-bar" :style="{ width: (animeResult.progressBarValue * 100).toFixed(1) + '%' }"></div>
            </template>
            <template v-else>
              ...
            </template>
          </td>
          <td role="cell" aria-colindex="4" class="table-col-main">
            {{ animeResult ? resultFormatters[0](animeResult.result) : '...' }}
          </td>
          <td role="cell" aria-colindex="5" class="table-col-extra" v-if="hasExtraResult">
            {{ animeResult ? resultFormatters[1](animeResult.extraResult) : '...' }}
          </td>
        </tr>
      </tbody>
    </table>
    <div class="text-end text-smaller">
      <router-link :to="fullResultsRoute">To full results »</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { Vue, Options } from 'vue-class-component';
import { AnimeData, ResultsType } from '@/util/data';
import { getResultTypeFormatter, getResultTypeName } from '@/util/helpers';
import { RouteLocationNormalized } from 'vue-router';

@Options({
  components: {
    AnimeNames,
    AnimeImages,
  },
  props: {
    ranking: Array, // { anime: AnimeData, result: number, extraResult: number }[]
    resultTypes: Array,
    isAnimeSeries: {
      type: Boolean,
      default: true,
    }, // Only used for the link
    top: Number,
    bottom: Number, // Optional
  },
})
export default class SimpleResultsTable extends Vue { // TODO: Replace this class with the AnimeTable component
  ranking!: { anime: AnimeData, result: number, extraResult?: number }[];
  resultTypes!: ResultsType[];
  isAnimeSeries!: boolean;
  top!: number;
  bottom?: number;

  processedRanking: ({ anime: AnimeData, result: number, extraResult?: number, progressBarValue: number, rank: number } | null)[] = [];
  resultNames: string[] = []; // [resultName, extraResultName]
  resultFormatters: ((value: number) => string)[] = []; // [resultFormatter, extraResultFormatter]

  hasExtraResult = false;

  get fullResultsRoute(): Partial<RouteLocationNormalized> {
    return {
      name: 'SurveyResultsFull',
      query: { [this.isAnimeSeries ? 'sortSeries' : 'sortSpecial']: this.resultTypes[0].toString() },
      hash: this.isAnimeSeries ? '#tableSeries' : '#tableSpecial',
    };
  }

  created(): void {
    this.hasExtraResult = this.resultTypes.length === 2;

    for (let resultType of this.resultTypes) {
      this.resultNames.push(getResultTypeName(resultType));
      this.resultFormatters.push(getResultTypeFormatter(resultType));
    }

    let progressBarMin: number;
    let progressBarMax: number;
    let progressBarValueParser = (value: number) => value;

    switch (this.resultTypes[0]) {
      case ResultsType.SCORE:
      case ResultsType.SCORE_MALE:
      case ResultsType.SCORE_FEMALE:
        progressBarMin = 1.0;
        progressBarMax = 5.0;
        break;
      case ResultsType.GENDER_SCORE_DIFFERENCE:
        progressBarMin = 0;
        progressBarMax = 1.5;
        progressBarValueParser = value => Math.abs(value);
        break;
      case ResultsType.GENDER_POPULARITY_RATIO:
        progressBarMin = 0;
        progressBarMax = 10.0;
        progressBarValueParser = value => value >= 1.0 ? value : 1.0 / value;
        break;
      case ResultsType.AGE:
        progressBarMin = 20.0;
        progressBarMax = 30.0;
        break;
      default: // For percentages
        progressBarMin = 0;
        progressBarMax = 0.85;
        break;
    }

    function progressBarValueFn(result: number) {
      const progressBarValue = (progressBarValueParser(result) - progressBarMin) / (progressBarMax - progressBarMin);
      return Math.max(Math.min(progressBarValue, 1), 0);
    }

    for (let rowIdx = 0; rowIdx < this.top; rowIdx++) {
      const row = this.ranking[rowIdx];
      this.processedRanking.push(Object.assign({
        progressBarValue: progressBarValueFn(row.result),
        rank: rowIdx + 1,
      }, row));
    }

    if (this.bottom != null) {
      this.processedRanking.push(null);

      for (let rowIdx = this.ranking.length - this.bottom; rowIdx < this.ranking.length; rowIdx++) {
        const row = this.ranking[rowIdx];
        this.processedRanking.push(Object.assign({
          progressBarValue: progressBarValueFn(row.result),
          rank: rowIdx + 1,
        }, row));
      }
    }
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
  z-index: 10;
}
.table-col-main {
  width: 10%!important;
  position: relative!important;
  text-align: right!important;
}
.table-col-extra {
  width: 7%!important;
  font-size: 80%;
  position: relative!important;
  text-align: right!important;
}
.table-row-progress-bar {
  position: absolute;
  top: 10%;
  height: 80%;
  z-index: -10;
  background-color: #bbdaf9;
}

td {
  vertical-align: middle;
}
</style>