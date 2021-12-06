<template>
  <div class="row align-items-center py-2 fw-bold" lang="en">
    <div class="col col-0-5"></div>
    <div class="col col-2"></div>
    <div class="col">Anime</div>
    <div class="col col-2 text-end">{{ resultNames[0] }}</div>
    <div class="col col-1-5 text-end text-smaller" v-if="hasExtraResult">{{ resultNames[1] }}</div>
  </div>
  <div class="row align-items-center hoverable py-1" v-for="(animeResult, idx) in ranking.slice(0, top ?? undefined)" :key="idx">
    <div class="col col-0-5">
      #{{ idx + 1 }}
    </div>
    <div class="col col-2 justify-content-center d-flex">
      <AnimeImages :animeImages="animeResult.anime.images" :enableCarouselControls="false" maxHeight="7.5em"/>
    </div>
    <div class="col">
      <AnimeNames :animeNames="animeResult.anime.names" :showShortName="false"/>
    </div>
    <div class="col col-2 text-end">
      {{ resultFormatters[0](animeResult.result) }}
    </div>
    <div class="col col-1-5 text-end text-smaller" v-if="hasExtraResult">
      {{ resultFormatters[1](animeResult.extraResult) }}
    </div>
  </div>
</template>

<script lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { Vue, Options } from 'vue-class-component';
import { ResultsType } from '@/util/data';

@Options({
  components: {
    AnimeNames,
    AnimeImages,
  },
  props: {
    ranking: Array, // { anime: AnimeData, result: number, extraResult: number }[]
    resultTypes: Array,
    top: Number,
  },
})
export default class SimpleResultsTable extends Vue {
  resultTypes!: ResultsType[];
  resultNames: string[] = [];
  resultFormatters: ((value: number) => string)[] = [];

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
  }

  private percentageFormatter(value: number): string {
    if (!value) return this.invalidValue;
    return value.toFixed(1) + '%';
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