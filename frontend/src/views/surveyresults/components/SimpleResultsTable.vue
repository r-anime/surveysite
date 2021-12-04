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

  private readonly resultTypeDataMap: Partial<Record<ResultsType, { name: string, formatter: (value: number) => string }>> = {
    // Someone please tell me why "hyphens: auto" doesn't work unless I add hyphens manually
    [ResultsType.POPULARITY]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty', formatter: this.popularityFormatter },
    [ResultsType.POPULARITY_MALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Male)', formatter: this.popularityFormatter },
    [ResultsType.POPULARITY_FEMALE]: { name: 'Pop\u00ADu\u00ADlar\u00ADi\u00ADty (Fe\u00ADmale)', formatter: this.popularityFormatter },
    [ResultsType.GENDER_POPULARITY_RATIO]: { name: 'Gen\u00ADder Ra\u00ADtio', formatter: this.genderRatioFormatter },
    [ResultsType.GENDER_POPULARITY_RATIO_INV]: { name: 'Gen\u00ADder Ra\u00ADtio', formatter: value => this.genderRatioFormatter(value, true) },
    [ResultsType.SCORE]: { name: 'Sco\u00ADre', formatter: this.scoreFormatter },
  };

  created(): void {
    this.hasExtraResult = this.resultTypes.length === 2;

    for (let resultType of this.resultTypes) {
      this.resultNames.push(this.resultTypeDataMap[resultType]?.name ?? 'ERR');
      this.resultFormatters.push(this.resultTypeDataMap[resultType]?.formatter ?? (() => 'ERR'));
    }
  }

  private popularityFormatter(value: number): string {
    if (!value) return 'N/A';
    return value.toFixed(1) + '%';
  }

  private genderRatioFormatter(value: number, inverted = false): string {
    if (!value) return 'N/A';
    return value.toFixed(2) + ' ' + (inverted ? 'F:M' : 'M:F');
  }

  private scoreFormatter(value: number): string {
    if (!value) return 'N/A';
    return value.toFixed(2);
  }
}
</script>