<template>
  <table role="table" :aria-colcount="3 + resultNames.length" class="table table-hover table-borderless">
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
              <AnimeNames :animeNames="animeResult.anime.names" :showShortName="false"/>
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
</template>

<script lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { Vue, Options } from 'vue-class-component';
import { AnimeData, ResultsType } from '@/util/data';

@Options({
  components: {
    AnimeNames,
    AnimeImages,
  },
  props: {
    ranking: Array, // { anime: AnimeData, result: number, extraResult: number }[]
    resultTypes: Array,
    top: Number,
    bottom: Number, // Optional
  },
})
export default class SimpleResultsTable extends Vue { // TODO: Clean this class up
  ranking!: { anime: AnimeData, result: number, extraResult?: number }[]; // progessBarValue is set in this class
  resultTypes!: ResultsType[];
  top!: number;
  bottom?: number;

  processedRanking: ({ anime: AnimeData, result: number, extraResult?: number, progressBarValue: number, rank: number }|null)[] = [];
  resultNames: string[] = []; // [resultName, extraResultName]
  resultFormatters: ((value: number) => string)[] = []; // [resultFormatter, extraResultFormatter]

  hasExtraResult = false;

  private readonly invalidValue = 'N/A';

  private readonly resultTypeDataMap: Partial<Record<ResultsType, { name: string, formatter: (value: number) => string }>> = {
    // Someone please tell me why "hyphens: auto" doesn't work unless I add hyphens manually
    [ResultsType.POPULARITY]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty', formatter: this.percentageFormatter },
    [ResultsType.POPULARITY_MALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Male)', formatter: this.percentageFormatter },
    [ResultsType.POPULARITY_FEMALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Fe\u00ADmale)', formatter: this.percentageFormatter },
    [ResultsType.GENDER_POPULARITY_RATIO]: { name: 'Gen\u00ADder Ra\u00ADtio', formatter: this.genderRatioFormatter },
    [ResultsType.SCORE]: { name: 'Sco\u00ADre', formatter: this.numberFormatter },
    [ResultsType.SCORE_MALE]: { name: 'Sco\u00ADre (Male)', formatter: this.numberFormatter },
    [ResultsType.SCORE_FEMALE]: { name: 'Sco\u00ADre (Female)', formatter: this.numberFormatter },
    [ResultsType.GENDER_SCORE_DIFFERENCE]: { name: 'Score Diff.', formatter: this.scoreDiffFormatter },
    [ResultsType.AGE]: { name: 'Avg. Age', formatter: this.numberFormatter },
    [ResultsType.UNDERWATCHED]: { name: 'Un\u00ADder\u00ADwatch\u00ADed', formatter: this.percentageFormatter },
    [ResultsType.SURPRISE]: { name: 'Sur\u00ADprise', formatter: this.percentageFormatter },
    [ResultsType.DISAPPOINTMENT]: { name: 'Dis\u00ADa\u00ADppoint\u00ADment', formatter: this.percentageFormatter },
  };

  created(): void {
    this.hasExtraResult = this.resultTypes.length === 2;

    for (let resultType of this.resultTypes) {
      this.resultNames.push(this.resultTypeDataMap[resultType]?.name ?? 'ERR');
      this.resultFormatters.push(this.resultTypeDataMap[resultType]?.formatter ?? (() => 'ERR'));
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

  private percentageFormatter(value: number): string {
    if (!value) return this.invalidValue;
    return (value * 100).toFixed(1) + '%';
  }

  private genderRatioFormatter(value: number): string {
    if (!value) return this.invalidValue;

    const shouldInvert = value < 1;
    if (shouldInvert && value === 0) return this.invalidValue;
    return (shouldInvert ? 1 / value : value).toFixed(2) + ' ' + (shouldInvert ? 'F:M' : 'M:F');
  }

  private numberFormatter(value: number): string {
    if (!value) return this.invalidValue;
    return value.toFixed(2);
  }

  private scoreDiffFormatter(value: number): string {
    if (!value) return this.invalidValue;

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