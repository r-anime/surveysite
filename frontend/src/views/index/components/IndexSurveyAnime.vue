<template>
  <div class="row align-items-center text-smaller-2">
    <div class="col-lg-4 col-sm-2 col-3">
      <AnimeImagesComponent :animeImages="animeResults.anime.images" maxHeight="5rem"/>
    </div>
    <div class="col ps-0" v-if="animeResults.anime.names">
      <AnimeNamesComponent :animeNames="animeResults.anime.names"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import AnimeNamesComponent from '@/components/AnimeNamesComponent.vue';
import AnimeImagesComponent from '@/components/AnimeImagesComponent.vue';
import type { IndexSurveyAnimeData } from '../data/index-survey-anime-data';

defineProps<{
  animeResults: IndexSurveyAnimeData;
}>();
</script>
