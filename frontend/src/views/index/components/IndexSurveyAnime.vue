<template>
  <div class="row align-items-center text-smaller-2">
    <div class="col-lg-4 col-sm-2 col-3">
      <AnimeImages :animeImages="animeResults.anime.images" :enableCarouselControls="false" maxHeight="5rem"/>
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
