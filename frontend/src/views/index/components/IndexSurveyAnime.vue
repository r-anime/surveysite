<template>
  <div class="row align-items-center">
    <div class="col col-2">
      <AnimeImages :animeImages="animeResults.anime.images" :enableCarouselControls="false"/>
    </div>
    <div class="col ps-0" v-if="animeResults.anime.names">
      <AnimeNames :animeNames="animeResults.anime.names" :showShortName="false"/>
    </div>
  </div>
</template>

<script lang="ts">
import AnimeNames from '@/components/AnimeNames.vue';
import AnimeImages from '@/components/AnimeImages.vue';
import { Options, Vue } from 'vue-class-component';

@Options({
  components: {
    AnimeNames,
    AnimeImages,
  },
  props: {
    animeResults: Object,
  },
})
export default class IndexSurveyAnime extends Vue {}
</script>
