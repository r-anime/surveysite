<template>
  <div class="row align-items-center hoverable py-2" v-for="(animeResult, idx) in ranking.slice(0, top ?? undefined)" :key="idx">
    <div class="col col-0-5">
      #{{ idx + 1 }}
    </div>
    <div class="col col-2 justify-content-center d-flex">
      <AnimeImages :animeImages="animeResult.anime.images" :enableCarouselControls="false" maxHeight="7.5em"/>
    </div>
    <div class="col">
      <AnimeNames :animeNames="animeResult.anime.names" :showShortName="false"/>
    </div>
    <div class="col col-1">
      {{ animeResult.result?.toFixed(2) ?? 'N/A' }}
    </div>
  </div>
</template>

<script lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { Vue, Options } from 'vue-class-component';

@Options({
  components: {
    AnimeNames,
    AnimeImages,
  },
  props: {
    ranking: Object, // { anime: AnimeData, result: number }
    top: Number,
  },
})
export default class SimpleResultsTable extends Vue {}
</script>